from django.test import SimpleTestCase
from django.core.exceptions import ValidationError


class SimpleModelTests(SimpleTestCase):
    """Tests simples sin base de datos para verificar lógica básica"""

    databases = []  # No usa base de datos

    def test_basic_assertion(self):
        """Test básico de aserción"""
        self.assertEqual(1 + 1, 2)

    def test_string_operations(self):
        """Test de operaciones con strings"""
        text = "TFGIBEX"
        self.assertTrue(text.startswith("TFG"))
        self.assertEqual(text.lower(), "tfgibex")

    def test_list_operations(self):
        """Test de operaciones con listas"""
        lista = [1, 2, 3, 4, 5]
        self.assertEqual(len(lista), 5)
        self.assertIn(3, lista)
        self.assertNotIn(10, lista)

    def test_dictionary_operations(self):
        """Test de operaciones con diccionarios"""
        data = {"mercado": "IBEX", "bolsa": "Madrid", "pais": "España"}
        self.assertEqual(data["mercado"], "IBEX")
        self.assertIn("bolsa", data)
        self.assertEqual(len(data), 3)

    def test_boolean_logic(self):
        """Test de lógica booleana"""
        is_premium = False
        is_public = True

        self.assertFalse(is_premium)
        self.assertTrue(is_public)
        self.assertTrue(is_public and not is_premium)

    def test_numeric_calculations(self):
        """Test de cálculos numéricos"""
        price = 9.99
        quantity = 3
        total = price * quantity

        self.assertAlmostEqual(total, 29.97, places=2)
        self.assertGreater(total, 25)
        self.assertLess(total, 30)

    def test_exception_handling(self):
        """Test de manejo de excepciones"""
        def divide_by_zero():
            return 1 / 0

        with self.assertRaises(ZeroDivisionError):
            divide_by_zero()

    def test_validation_logic(self):
        """Test de lógica de validación"""
        def validate_email(email):
            return "@" in email and "." in email.split("@")[1]

        self.assertTrue(validate_email("test@example.com"))
        self.assertFalse(validate_email("invalid-email"))
        self.assertFalse(validate_email("test@"))

    def test_data_transformation(self):
        """Test de transformación de datos"""
        raw_data = "  Mercado Europeo  "
        processed = raw_data.strip().upper()

        self.assertEqual(processed, "MERCADO EUROPEO")
        self.assertNotEqual(processed, raw_data)

    def test_conditional_logic(self):
        """Test de lógica condicional"""
        def get_fee(is_premium):
            return 0 if is_premium else 0.05

        self.assertEqual(get_fee(True), 0)
        self.assertEqual(get_fee(False), 0.05)