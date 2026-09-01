from wordserver.resuming import resume_point


def test_an_absent_header_resumes_from_the_start() -> None:
    assert resume_point(None) == 0


def test_an_empty_header_resumes_from_the_start() -> None:
    assert resume_point("") == 0


def test_a_seen_id_resumes_from_the_frame_after_it() -> None:
    assert resume_point("31") == 32


def test_a_folded_pair_resumes_from_the_earlier_frame() -> None:
    assert resume_point("21, 32") == 22


def test_surrounding_space_is_ignored() -> None:
    assert resume_point(" 7 ") == 8


def test_a_trailing_separator_leaves_the_id_readable() -> None:
    assert resume_point("12,") == 13


def test_an_unreadable_header_resumes_from_the_start() -> None:
    assert resume_point("abc") == 0


def test_a_signed_id_is_unreadable() -> None:
    assert resume_point("-1") == 0


def test_a_readable_id_survives_unreadable_company() -> None:
    assert resume_point("abc, 32") == 33
