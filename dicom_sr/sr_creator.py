from pydicom.dataset import Dataset, FileDataset
from pydicom.sequence import Sequence
from pydicom.filereader import dcmread
from pydicom.uid import generate_uid, ExplicitVRLittleEndian

from datetime import datetime

from pathlib import Path

BASIC_TEXT_SR_SOP_CLASS = "1.2.840.10008.5.1.4.1.1.88.11" # sr sop

def make_sr_dicom(report_text: str, ref_dicom_path: str):
    ref = dcmread(ref_dicom_path) 

    file_meta = Dataset()
    file_meta.MediaStorageSOPClassUID = BASIC_TEXT_SR_SOP_CLASS
    file_meta.MediaStorageSOPInstanceUID = generate_uid()
    file_meta.TransferSyntaxUID = ExplicitVRLittleEndian #인코딩 방법.(가장 기본 포맷)
    # (선택) 구현 식별자
    file_meta.ImplementationClassUID = "1.2.826.0.1.3680043.10.1234"  #회사 소프트웨어 고유 oid루트

    ds = FileDataset(None, {}, file_meta=file_meta, preamble=b"\0" * 128) #128바이트 공간두고 preamble에 dicm붙이게 해줌. 인식하는데 도움
    ds.is_little_endian = True
    ds.is_implicit_VR = False
    ds.SpecificCharacterSet = "ISO_IR 192"  # UTF-8

    ds.PatientName  = getattr(ref, "PatientName", "")
    ds.PatientID    = getattr(ref, "PatientID", "")
    ds.PatientBirthDate = getattr(ref, "PatientBirthDate", "")
    ds.PatientSex   = getattr(ref, "PatientSex", "")

    ds.StudyInstanceUID = getattr(ref, "StudyInstanceUID", generate_uid())
    ds.StudyDate   = getattr(ref, "StudyDate", "")
    ds.StudyTime   = getattr(ref, "StudyTime", "")
    ds.AccessionNumber = getattr(ref, "AccessionNumber", "")
    ds.StudyID     = getattr(ref, "StudyID", "")

    ds.Modality = "SR"
    ds.SeriesInstanceUID = generate_uid() #시리즈 구분하는 id (한 사람 study에서 dcm인지 sr인지)
    ds.SeriesNumber = 9000  # 한사람 한 study안에서 여러개 sr중 구분하는 방법, sr은 9000번 부터 시작

    ds.Manufacturer = getattr(ref, "Manufacturer", "") #dcm  객체 생성한 제조사

    ds.SOPClassUID = BASIC_TEXT_SR_SOP_CLASS
    ds.SOPInstanceUID = file_meta.MediaStorageSOPInstanceUID

    # --- SR Document ---
    now = datetime.now()
    ds.InstanceNumber = 1
    ds.ContentDate = now.strftime("%Y%m%d")
    ds.ContentTime = now.strftime("%H%M%S")
    ds.CompletionFlag = "COMPLETE"    # 개발/테스트 단계
    ds.VerificationFlag = "UNVERIFIED"  # 개발/테스트 단계

    root = Dataset()
    root.ValueType = "CONTAINER"
    root.ContinuityOfContent = "SEPARATE"
    # 루트에는 RelationshipType 넣지 않음(루트는 상위가 없음)
    root.ConceptNameCodeSequence = Sequence([Dataset()])
    root.ConceptNameCodeSequence[0].CodeValue = "18748-4"         # LOINC: Diagnostic Imaging Report
    root.ConceptNameCodeSequence[0].CodingSchemeDesignator = "LN"
    root.ConceptNameCodeSequence[0].CodeMeaning = "Diagnostic Imaging Report"

    # 본문 텍스트 1개 (필요시 'Impression' 등 더 추가 가능)
    text_item = Dataset()
    text_item.ValueType = "TEXT"
    text_item.RelationshipType = "CONTAINS"
    text_item.ConceptNameCodeSequence = Sequence([Dataset()])
    text_item.ConceptNameCodeSequence[0].CodeValue = "121071"     # DCM: Finding
    text_item.ConceptNameCodeSequence[0].CodingSchemeDesignator = "DCM"
    text_item.ConceptNameCodeSequence[0].CodeMeaning = "Finding"
    text_item.TextValue = report_text

    root.ContentSequence = Sequence([text_item])
    ds.ContentSequence = Sequence([root])

    # 저장
    out_dir = '../saved_sr'
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    pid = ds.PatientID
    sn = ds.SeriesNumber
    save_path = Path(out_dir) / f'{pid}_{sn}_sr.dcm'
    ds.save_as(save_path, write_like_original=False)
    return ds, save_path
