import requests

def send_to_pacs(dicom_file, orthanc_url="http://localhost:8042", username="orthanc", password="orthanc"):
    with open(dicom_file, 'rb') as f:
        files = {'file': f}
        response = requests.post(
            f"{orthanc_url}/instances",
            files=files,
            auth=(username, password)
        )
    if response.status_code == 200:
        print(f"[SUCCESS] SR uploaded to Orthanc: {response.json().get('ID')}")
    else:
        print(f"[ERROR] Failed to upload SR: {response.status_code} - {response.text}")
