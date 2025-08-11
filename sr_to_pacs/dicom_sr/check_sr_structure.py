from pydicom.filereader import dcmread

def walk_content(items, indent=0):
    for it in items:
        vt = getattr(it, "ValueType", "")
        name = ""
        if hasattr(it, "ConceptNameCodeSequence"):
            cnc = it.ConceptNameCodeSequence[0]
            name = f"{cnc.CodeMeaning} ({cnc.CodeValue}:{cnc.CodingSchemeDesignator})"
        prefix = "  " * indent + f"[{vt}] {name}"
        if vt == "TEXT":
            print(prefix, "->", it.TextValue)
        else:
            print(prefix)
        if hasattr(it, "ContentSequence"):
            walk_content(it.ContentSequence, indent+1)

def check_content(path) :
  ds = dcmread(path)
  print("Modality:", ds.Modality)
  print("SOPClassUID:", ds.SOPClassUID)
  print("SpecificCharacterSet:", ds.get("SpecificCharacterSet", ""))
  print("StudyInstanceUID:", ds.StudyInstanceUID)
  print("SeriesInstanceUID:", ds.SeriesInstanceUID)
  print("SeriesNumber:", ds.get("SeriesNumber", None))
  print("CompletionFlag:", ds.CompletionFlag, "VerificationFlag:", ds.VerificationFlag)

  root_items = ds.ContentSequence
  walk_content(root_items)
