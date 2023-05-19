import pytest

# Reader imports
import copybook

#
# Tests
#
tests = {
"extra header text":"""
       10 IDENTIFICATION DIVISION.
       PROGRAM-ID. 8-REPORT.
	   AUTHOR. DDT. MODIFIED BY OREN.
	   DATE WRITTEN. 10/13/2010.
	   DATE COMPILED. 10/13/2010.
       01  WORK-BOOK.                                                             
       10  TAX-RATE              PIC 9(3).
""",
"no header text":"""
       01  RECORD.                                                             
        05  TAX-RATE              PIC 9(3).
""",
"numeric pic no precision":"""
       01  WORK-BOOK.                                                             
       10  TAX-RATE              PIC 9(3).
""",
"numeric pic precision only":"""
       01  WORK-BOOK.                                                             
       10  TAX-RATE              PIC V9(3).
""",
"numeric pic length and precision":"""
       01  WORK-BOOK.                                                             
        10  TAX-RATE              PIC 9(13)V9(3).
""",
"numeric pic length and precision with dot":"""
       01  WORK-BOOK.                                                             
        10  TAX-RATE              PIC 9(13).9(3).
""",
"numeric pic signed S":"""
       01  WORK-BOOK.                                                             
        10  TAX-RATE              PIC S9(13)V9(3).
""",
"numeric pic signed minus":"""
       01  WORK-BOOK.                                                             
        10  TAX-RATE              PIC -9(13)V9(3).
""",
"numeric pic with 9s":"""
       01  WORK-BOOK.                                                             
        10  TAX-RATE              PIC 9999.
""",
"numeric pic with 9s and precision":"""
       01  WORK-BOOK.                                                             
        10  TAX-RATE              PIC 9(2)V99.
""",
"numeric pic with 9s and precision and sign":"""
       01  WORK-BOOK.                                                             
        10  TAX-RATE              PIC -9999.99.
""",
"numeric pic with 9s and precision and separate sign":"""
       01  WORK-BOOK.                                                             
        10  TAX-RATE        PIC S9(13)V9(2)                
                    SIGN TRAILING SEPARATE.                                     
""",
"numeric pic with 9s and precision and separate leading sign":"""
       01  WORK-BOOK.                                                             
        10  TAX-RATE        PIC S9(13)V9(2)                
                    SIGN LEADING SEPARATE.                                     
""",
"numeric pic signed with leading literal decimal":"""
       01  WORK-BOOK.                                                             
        10  TAX-RATE              PIC +.999.
""",
"numeric pic signed with leading implied decimal":"""
       01  WORK-BOOK.                                                             
        10  TAX-RATE              PIC +V999.
""",
"string pic with leading 0s":"""
       01  WORK-BOOK.                                                             
        10  TAX-RATE        PIC X(005).
""",

}

valueParseTests = [
    {"description": "string literal", "pic": "X(6)", "clause": "\"HELLO!\"", "expect": "HELLO!"},
    {"description": "spaces", "pic": "X(6)", "clause": "SPACES", "expect": "      "},
    {"description": "space", "pic": "X(1)", "clause": "SPACE", "expect": " "},
    {"description": "zeros", "pic": "9(6)", "clause": "ZEROS", "expect": "000000"},
    {"description": "zeroes", "pic": "9(6)", "clause": "ZEROES", "expect": "000000"},
    {"description": "zero", "pic": "9(1)", "clause": "ZERO", "expect": "0"},
    {"description": "hex constant", "pic": "X(1)", "clause": "X'05'", "expect": "05"}
]

from pyparsing import ParseException
def test_parse_string():
    failed =0
    for test_name,test in tests.items():
        print(test_name)
        try:
            root = copybook.parse_string(test)
        except ParseException as pe:
            failed += 1
            print(f"test failed: {test_name}")
            print(pe)
    assert failed==0

def test_string_pic_with_leading_0s():
    result = copybook.parse_string(tests["string pic with leading 0s"]).flatten()
    assert len(result)==2
    assert type(result[1])==copybook.Field
    assert result[1].datatype=='str'
    assert result[1].length==5
    assert result[1].get_total_length()==5
    assert result[1].start_pos==0

def test_redefines_field():
    test_str = """
       01 POLICY.
           05 POLICY-KEY  PIC 9(5).
           05 POLICY-HOLDER-KEY  PIC 9(10).
           05 PRODUCT-KEY REDEFINES POLICY-HOLDER-KEY PIC X(10).
    """
    result = copybook.parse_string(test_str).flatten()
    assert len(result)==4
    assert [type(i) for i in result]==[copybook.FieldGroup,copybook.Field,copybook.Field,copybook.Field]
    assert result[2].datatype=='int' and result[3].datatype=='str'
    assert result[1].length==5 and result[2].length==10 and result[3].length==10
    assert result[0].get_total_length()==15
    assert result[2].get_total_length()==10 and result[3].get_total_length()==10
    assert [i.start_pos for i in result]==[0,0,5,5]

def test_occurs_field():
    test_str = """
       01 POLICY.
         05 POLICY-KEY         PIC 9(10).
         05 ROW-EFFECTIVE-DT   OCCURS 3 TIMES PIC 9(8).
     """
    result = copybook.parse_string(test_str).flatten()
    assert len(result)==5
    assert [type(i) for i in result]==[copybook.FieldGroup,copybook.Field,copybook.Field,copybook.Field,copybook.Field]
    assert result[0].get_total_length()==10+8*3
    assert [i.start_pos for i in result]==[0,0,10,18,26]

def test_char_x_pic():
    test_str = """
       01  WORK-BOOK.
         10 TAX-RATE PIC S9(13)V9(2) SIGN LEADING SEPARATE.
         10  AMOUNT        PIC X(2).
         10  AMOUNT2       PIC S9(4)V9(2).
     """
    result = copybook.parse_string(test_str).flatten()
    assert len(result)==4
    assert result[2].datatype=="str"
    assert result[2].get_total_length()==2

def test_extended_char_pic():
    test_str = """
       01  WORK-BOOK.
         10 TAX-RATE PIC S9(13)V9(2) SIGN LEADING SEPARATE.
         10  AMOUNT        PIC XX.
         10  AMOUNT2       PIC S9(4)V9(2).
     """
    result = copybook.parse_string(test_str).flatten()
    assert len(result)==4
    assert result[2].datatype=="str"
    assert result[2].get_total_length()==2

def test_value_clauses():
    failed_tests = []
    for test in valueParseTests:
        copybook_sample = None
        try:
            pic_clause = test["pic"]
            expected_datatype = "str"
            if "V9(" in pic_clause or "." in pic_clause:
                expected_datatype = "decimal"
            elif "S9" in pic_clause or pic_clause.strip()[0] == "9":
                expected_datatype = "int"
            value_clause = test["clause"]
            copybook_sample = f"""
               01  WORK-BOOK.
                 10  WS-TEST       PIC {pic_clause} VALUE {value_clause}.
            """
            result = copybook.parse_string(copybook_sample).flatten()
            assert len(result) == 2
            assert result[1].datatype == expected_datatype
            #assert result[1].get_total_length() == 1
            assert result[1].default_value == test["expect"]
        except (AssertionError, ParseException) as e:
            description = test["description"]
            failed_tests.append(description)
            print(f"test_value_clauses {description} failure: {e}")
            print(copybook_sample)
    assert len(failed_tests) == 0

def test_plus_sign_control_symbol():
    test_str = """
       01  WORK-BOOK.
         10  AMOUNT2       PIC +9(4).99.
    """
    result = copybook.parse_string(test_str).flatten()
    assert len(result)==2
    assert result[1].datatype=="decimal"
    assert result[1].get_total_length()==8

def test_minus_sign_control_symbol():
    test_str = """
       01  WORK-BOOK.
         10  AMOUNT2       PIC -9(4).99.
    """
    result = copybook.parse_string(test_str).flatten()
    assert len(result)==2
    assert result[1].datatype=="decimal"
    assert result[1].get_total_length()==8

def test_explicit_decimal():
    test_str = """
       01  WORK-BOOK.
         10  AMOUNT2       PIC 9(4).99.
    """
    result = copybook.parse_string(test_str).flatten()
    assert len(result)==2
    assert result[1].datatype=="decimal"
    assert result[1].explicit_decimal == True
    assert result[1].get_total_length()==7

def test_signed_leading_literal_decimal():
    test_str = """
       01  WORK-BOOK.
         10  AMOUNT2       PIC +.9(7).
    """
    result = copybook.parse_string(test_str).flatten()
    assert len(result)==2
    assert result[1].datatype=="decimal"
    assert result[1].explicit_decimal == True
    assert result[1].get_total_length()==9


def test_signed_leading_implied_decimal():
    test_str = """
       01  WORK-BOOK.
         10  AMOUNT2       PIC +V9(7).
    """
    result = copybook.parse_string(test_str).flatten()
    assert len(result)==2
    assert result[1].datatype=="decimal"
    assert result[1].explicit_decimal == False
    assert result[1].get_total_length()==8
