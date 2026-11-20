import json
import tempfile
import unittest
from pathlib import Path

from src.busca import (carregar_base, buscar_por_id, buscar_por_tema,
                       buscar_por_palavras_chave, listar_temas, temas_relacionados)


class TestBusca(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = carregar_base()

    def test_consultas(self):
        casos = [
            ("CPF", 1), ("Como consultar meu cpf?", 1),
            ("tirar CIN", 2), ("CARTEIRA DE TRABALHO", 3),
            ("titulo de eleitor", 4), ("CNH", 5), ("cadunico", 6),
            ("bolsa familia", 7), ("INSS", 8), ("gov.br", 9),
            ("estacionamento idoso", 10), ("Procon", 11),
            ("violencia contra a mulher", 12), ("maus-tratos animais", 13),
            ("PCD", 14), ("seguro-desemprego", 15),
        ]
        for consulta, esperado in casos:
            with self.subTest(consulta=consulta):
                self.assertEqual(buscar_por_palavras_chave(self.base, consulta)[0]["id"], esperado)

    def test_sem_resultados(self):
        for consulta in ["", "   ", "???", "como consultar", "receita de bolo", None]:
            with self.subTest(consulta=consulta):
                self.assertEqual(buscar_por_palavras_chave(self.base, consulta), [])

    def test_identificadores(self):
        self.assertEqual(buscar_por_id(self.base, " 1 ")["id"], 1)
        for valor in [True, 1.2, "abc", "1.0", 999, None]:
            self.assertIsNone(buscar_por_id(self.base, valor))

    def test_temas_e_navegacao(self):
        self.assertEqual(len(listar_temas(self.base)), 3)
        self.assertEqual(len(buscar_por_tema(self.base, "DOCUMENTACAO")), 5)
        self.assertEqual(buscar_por_tema(self.base, "inexistente"), [])
        for tema in listar_temas(self.base):
            relacionados = temas_relacionados(self.base, tema)
            self.assertEqual(len(relacionados), 2)
            for relacao in relacionados:
                self.assertTrue(buscar_por_tema(self.base, relacao["tema"]))

    def test_filtro_e_multiplos_resultados(self):
        resultados = buscar_por_palavras_chave(self.base, "denuncia")
        self.assertEqual([r["id"] for r in resultados], [11, 12, 13])
        self.assertEqual(buscar_por_palavras_chave(self.base, "cpf", "Serviços Públicos"), [])

    def test_base_invalida(self):
        with tempfile.TemporaryDirectory() as pasta:
            caminho = Path(pasta) / "base.json"
            with self.assertRaises(ValueError):
                carregar_base(caminho)
            for conteudo in ["", "{", "[]", "{}", '[{"id": 1}]',
                             json.dumps([self.base[0], self.base[0]])]:
                caminho.write_text(conteudo, encoding="utf-8")
                with self.subTest(conteudo=conteudo), self.assertRaises(ValueError):
                    carregar_base(caminho)


if __name__ == "__main__":
    unittest.main()
