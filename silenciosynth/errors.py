class SilencioSynthError(RuntimeError):
    pass


class CatalogError(SilencioSynthError):
    pass


class IntegrityError(SilencioSynthError):
    pass


class RuntimeContractError(SilencioSynthError):
    pass
