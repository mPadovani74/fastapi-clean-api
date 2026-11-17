import time
from collections import defaultdict, deque
from threading import Lock


class LimitadorTentativas:

    def __init__(self, max_falhas: int = 5, janela_segundos: int = 15 * 60):
        self.max_falhas = max_falhas
        self.janela_segundos = janela_segundos
        self._falhas: dict[str, deque[float]] = defaultdict(deque)
        self._lock = Lock()

    def _limpar(self, chave: str, agora: float) -> None:
        """Descarta falhas fora da janela. Chamar já com o lock."""
        falhas = self._falhas.get(chave)
        if falhas is None:
            return
        while falhas and agora - falhas[0] > self.janela_segundos:
            falhas.popleft()
        if not falhas:
            del self._falhas[chave]

    def bloqueado(self, chave: str) -> bool:
        agora = time.monotonic()
        with self._lock:
            self._limpar(chave, agora)
            return len(self._falhas.get(chave, ())) >= self.max_falhas

    def registrar_falha(self, chave: str) -> None:
        agora = time.monotonic()
        with self._lock:
            self._limpar(chave, agora)
            self._falhas[chave].append(agora)

    def zerar(self, chave: str) -> None:
        with self._lock:
            self._falhas.pop(chave, None)

limitador = LimitadorTentativas()
