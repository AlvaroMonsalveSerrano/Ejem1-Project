# Tests del punto de entrada principal; verifica la salida por stdout.
from ejem1.main import main


def test_main(capsys):
    main()
    captured = capsys.readouterr()
    assert captured.out == "Hola, mundo!\n"
