import pytest

from contador_fp.contracts import (
    ContractError,
    ensure,
    invariant,
    require,
    validate_fp_result,
    validate_processing_invariants,
)


def test_require_materializes_precondition():
    with pytest.raises(ContractError):
        require(False, "pre-condicao violada")


def test_ensure_materializes_postcondition():
    with pytest.raises(ContractError):
        ensure(False, "pos-condicao violada")


def test_invariant_materializes_processing_invariant():
    with pytest.raises(ContractError):
        invariant(False, "invariante violada")


def test_validate_fp_result_rejects_invalid_postcondition():
    with pytest.raises(ContractError):
        validate_fp_result({"Total_SFP": -1, "Elementos_FP": []})


def test_validate_processing_invariants_rejects_invalid_state():
    with pytest.raises(ContractError):
        validate_processing_invariants({"Total_SFP": 0, "Elementos_FP": "invalido"})
