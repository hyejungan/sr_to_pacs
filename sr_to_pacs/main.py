from dicom_sr.sr_creator import make_sr
from send_to_pacs.cstore_sender import send_to_pacs

report_text = "위 전정부에 궤양성 병변. 조직검사 시행. 3개월 후 추적 내시경 권장."
sr_path = "reports/auto_report_sr.dcm"

# SR 생성
ds = make_sr(patient_id="123456", patient_name="TEST^PATIENT", report_text=report_text)
ds.save_as(sr_path)

# PACS 전송
send_to_pacs(dicom_file=sr_path)
