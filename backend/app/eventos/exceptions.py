class EventoNaoEncontradoException(Exception):
    def __init__(self, evento_id: int):
        super().__init__(f"Evento {evento_id} não encontrado")
        self.evento_id = evento_id
