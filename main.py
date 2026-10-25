import flet as ft

from emydocx.app import EmyDocxApp

def main(page: ft.Page) -> None:
    EmyDocxApp(page)

if __name__ == "__main__":
    ft.run(main)