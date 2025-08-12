from dicom_sr.sr_creator import make_sr_dicom
from dicom_sr.check_sr_structure import check_content
from send_to_pacs.cstore_sender import send_to_pacs

report_text = "위 전정부에 궤양성 병변. 조직검사 시행. 3개월 후 추적 내시경 권장."
ref_path = "reports/1.dcm"

# 1. SR 생성
ds, file_path = make_sr_dicom(report_text=report_text, ref_dicom_path=ref_path)

# 2. PACS 전송
send_to_pacs(dicom_file=file_path)

# 3. 전송된 파일 구조 확인하기
check_content(file_path)
