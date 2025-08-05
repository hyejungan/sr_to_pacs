from pydicom.dataset import Dataset, FileDataset
from pydicom.sequence import Sequence
from pydicom.filereader import dcmread

def make_sr_dicom(report_text, ref_dicom_path, save_path):
    ref_ds = dcmread(ref_dicom_path)

    file_meta = Dataset()
    file_meta.MediaStorageSOPClassUID = ref_ds.file_meta.MediaStorageSOPClassUID
    file_meta.MediaStorageSOPInstanceUID = ref_ds.file_meta.MediaStorageSOPInstanceUID
    file_meta.TransferSyntaxUID = ref_ds.file_meta.TransferSyntaxUID

    ds = FileDataset(save_path, {}, file_meta=file_meta, preamble=b"\0" * 128)
    column_names = [elem.keyword for elem in ref_ds if elem.keyword]
    for name in column_names :
        ds[f'{name}'] = ref_ds[f'{name}']

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

    root = Dataset()
    root.ValueType = "CONTAINER"
    root.ContinuityOfContent = "SEPARATE"
    root.RelationshipType = ""
    root.ConceptNameCodeSequence = Sequence([Dataset()])
    root.ConceptNameCodeSequence[0].CodeValue = "18748-4"
    root.ConceptNameCodeSequence[0].CodingSchemeDesignator = "LN"
    root.ConceptNameCodeSequence[0].CodeMeaning = "Diagnostic Imaging Report"
    root.SpecificCharacterSet = 'ISO_IR 192'

    finding = Dataset()
    finding.ValueType = "TEXT"
    finding.RelationshipType = "CONTAINS"
    finding.ConceptNameCodeSequence = Sequence([Dataset()])
    finding.ConceptNameCodeSequence[0].CodeValue = "121071"
    finding.ConceptNameCodeSequence[0].CodingSchemeDesignator = "DCM"
    finding.ConceptNameCodeSequence[0].CodeMeaning = "Finding"
    finding.TextValue = report_text
    finding.SpecificCharacterSet = 'ISO_IR 192'

    root.ContentSequence = Sequence([finding])
    ds.ContentSequence = Sequence([root])

    return ds
