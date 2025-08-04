from pydicom.dataset import Dataset, FileDataset
from pydicom.sequence import Sequence
from pydicom.uid import generate_uid, ExplicitVRLittleEndian
from pydicom.filereader import dcmread
from datetime import datetime

def make_sr_dicom(report_text, ref_dicom_path, save_path, patient_id="123456", patient_name="TEST^PATIENT"):
    # 1. ref_dicom 로딩 → evidence로 넣음
    ref_ds = dcmread(ref_dicom_path)

    # 2. DICOM 메타 정보
    file_meta = Dataset()
    file_meta.MediaStorageSOPClassUID = "1.2.840.10008.5.1.4.1.1.88.33"  # Comprehensive SR
    file_meta.MediaStorageSOPInstanceUID = generate_uid()
    file_meta.TransferSyntaxUID = ExplicitVRLittleEndian

    # 3. SR DICOM 객체 생성
    ds = FileDataset(save_path, {}, file_meta=file_meta, preamble=b"\0" * 128)

    dt = datetime.now()
    ds.SOPClassUID = file_meta.MediaStorageSOPClassUID
    ds.SOPInstanceUID = file_meta.MediaStorageSOPInstanceUID
    ds.StudyInstanceUID = ref_ds.StudyInstanceUID if "StudyInstanceUID" in ref_ds else generate_uid()
    ds.SeriesInstanceUID = generate_uid()
    ds.Modality = "SR"
    ds.SeriesNumber = 1
    ds.InstanceNumber = 1
    ds.StudyDate = dt.strftime('%Y%m%d')
    ds.StudyTime = dt.strftime('%H%M%S')

    ds.PatientID = ref_ds.PatientID if "PatientID" in ref_ds else patient_id
    ds.PatientName = ref_ds.PatientName if "PatientName" in ref_ds else patient_name
    ds.PatientBirthDate = ref_ds.PatientBirthDate if "PatientBirthDate" in ref_ds else "19700101"

    # 4. Evidence Sequence
    ds.CurrentRequestedProcedureEvidenceSequence = Sequence([
        Dataset()
    ])
    ds.CurrentRequestedProcedureEvidenceSequence[0].StudyInstanceUID = ds.StudyInstanceUID
    ds.CurrentRequestedProcedureEvidenceSequence[0].ReferencedSeriesSequence = Sequence([
        Dataset()
    ])
    ds.CurrentRequestedProcedureEvidenceSequence[0].ReferencedSeriesSequence[0].SeriesInstanceUID = ref_ds.SeriesInstanceUID
    ds.CurrentRequestedProcedureEvidenceSequence[0].ReferencedSeriesSequence[0].ReferencedSOPSequence = Sequence([
        Dataset()
    ])
    ds.CurrentRequestedProcedureEvidenceSequence[0].ReferencedSeriesSequence[0].ReferencedSOPSequence[0].ReferencedSOPClassUID = ref_ds.SOPClassUID
    ds.CurrentRequestedProcedureEvidenceSequence[0].ReferencedSeriesSequence[0].ReferencedSOPSequence[0].ReferencedSOPInstanceUID = ref_ds.SOPInstanceUID

    # 5. SR 본문 구성 (Text Finding)
    root = Dataset()
    root.ValueType = "CONTAINER"
    root.ContinuityOfContent = "SEPARATE"
    root.RelationshipType = ""
    root.ConceptNameCodeSequence = Sequence([Dataset()])
    root.ConceptNameCodeSequence[0].CodeValue = "18748-4"
    root.ConceptNameCodeSequence[0].CodingSchemeDesignator = "LN"
    root.ConceptNameCodeSequence[0].CodeMeaning = "Diagnostic Imaging Report"

    finding = Dataset()
    finding.ValueType = "TEXT"
    finding.RelationshipType = "CONTAINS"
    finding.ConceptNameCodeSequence = Sequence([Dataset()])
    finding.ConceptNameCodeSequence[0].CodeValue = "121071"
    finding.ConceptNameCodeSequence[0].CodingSchemeDesignator = "DCM"
    finding.ConceptNameCodeSequence[0].CodeMeaning = "Finding"
    finding.TextValue = report_text

    root.ContentSequence = Sequence([finding])
    ds.ContentSequence = Sequence([root])

    # 6. 저장
    ds.save_as(save_path)
    print(f"✅ SR 저장 완료: {save_path}")
    return ds
