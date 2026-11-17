class CredenciaisInvalidas(Exception):
    def __init__(self):
        super().__init__("Credenciais inválidas")


class MuitasTentativas(Exception):
    def __init__(self):
        super().__init__("Muitas tentativas. Tente novamente mais tarde.")
