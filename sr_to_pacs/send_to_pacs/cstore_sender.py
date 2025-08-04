import requests

def send_to_pacs(dicom_file):
    with open(dicom_file, 'rb') as f:
        url = "http://localhost:8042/instances"  # 당신의 Orthanc URL
        headers = {'Content-Type': 'application/dicom'}
        response = requests.post(url, data=f, headers=headers)

    try:
        data = response.json()
        print(f"[SUCCESS] SR uploaded to Orthanc: {data.get('ID')}")
    except Exception as e:
        print("⚠️ Failed to decode JSON response from Orthanc")
        print("Status Code:", response.status_code)
        print("Raw Response:", response.text)
        print("Exception:", e)
