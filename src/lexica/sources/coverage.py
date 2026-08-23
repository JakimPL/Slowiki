from lexica.names import DictionaryName


def morphology_covers(name: DictionaryName) -> bool:
    match name:
        case DictionaryName.SJP | DictionaryName.OSPS:
            return True
        case DictionaryName.ENGLISH:
            return False
