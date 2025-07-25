from datetime import datetime
from pydicom import dcmread
from highdicom.sr import ComprehensiveSR
from highdicom.sr.value_types import TextContentItem
from highdicom.sr.coding import CodedConcept
from pydicom.uid import generate_uid
from send_to_pacs.cstore_sender import send_to_pacs

def make_sr(patient_id, patient_name, report_text, ref_dicom_path):
    ref_ds = dcmread(ref_dicom_path)

    item = TextContentItem(
        name=CodedConcept(value='121071', scheme_designator='DCM', meaning='Finding'),
        value=report_text,
        relationship_type='CONTAINS'
    )

    sr = ComprehensiveSR(
        evidence=[ref_ds],
        series_instance_uid=generate_uid(),
        series_number=1,
        instance_number=1,
        sop_instance_uid=generate_uid(),
        manufacturer='MyCompany',
        study_instance_uid=ref_ds.StudyInstanceUID,
        procedure_reported=CodedConcept(value='73761001', scheme_designator='SCT', meaning='Endoscopy'),
        content=[item],
        patient_id=patient_id,
        patient_name=patient_name,
        patient_birth_date='19700101',
        performed_procedure_step_start_datetime=datetime.now()
    )

    return sr

if __name__ == "__main__":
    report_text = "위 전정부에 궤양성 병변. 조직검사 시행. 3개월 후 추적 내시경 권장."
    patient_id = "123456"
    patient_name = "TEST^PATIENT"
    sr_path = "reports/auto_report_sr.dcm"
    ref_dicom_path = "ref.dcm"  # 참조 DICOM 파일 지정

    ds = make_sr(
        patient_id=patient_id,
        patient_name=patient_name,
        report_text=report_text,
        ref_dicom_path=ref_dicom_path
    )

    ds.save_as(sr_path)
    print(f"S{sr_path} 저장완료")

    send_to_pacs(sr_path)
