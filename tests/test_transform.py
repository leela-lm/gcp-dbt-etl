from src.etl.transform import extract_fields, transform_chapters, _clean_str, _fix_chapter_id

VALID = {
    "attributes": {
        "University_Chapter": "Florida State University",
        "City": "Tallahassee", "State": "FL",
        "ChapterID": "FL-0110"
    },
    "geometry": {"x": -84.30427, "y": 30.43811}
}

def test_valid_record():
    r = extract_fields(VALID)
    assert r["chapter_name"] == "Florida State University"
    assert r["city"]         == "Tallahassee"
    assert r["chapter_id"]   == "FL-0110"

def test_trailing_whitespace_stripped():
    assert _clean_str("Ruston ") == "Ruston"

def test_missing_hyphen_fixed():
    assert _fix_chapter_id("GA0147") == "GA-0147"
