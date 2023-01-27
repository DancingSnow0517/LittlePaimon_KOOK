class CallClass:

    def __init__(self) -> None:
        super().__init__()

    def __call__(self, *args, **kwargs):
        print(args)
        print(kwargs)
        print("Call class __call__ method")

    def a_method(self):
        print("Call class a_method")


if __name__ == '__main__':
    a = CallClass()  # Callable
    a.a_method()
    a('123', '123123', a='1', b='2')
    b = CallClass()
    b()
    ...