class InscricaoDuplicadaException(Exception):
    def __init__(self):
        super().__init__("Você já está inscrito neste evento")


class EventoLotadoException(Exception):
    def __init__(self, evento_id: int):
        super().__init__(f"O evento {evento_id} não tem mais vagas")
        self.evento_id = evento_id


class InscricaoNaoEncontradaException(Exception):
    def __init__(self):
        super().__init__("Inscrição não encontrada")
