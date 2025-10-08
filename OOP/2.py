


class LogOperation:
    def __init__(self):
        self.__in1 = False
        self.__in2 = False
        self._res = False
        self.__nextEl = None
        self.__nextIn = 0
        if not hasattr(self, "calc"):
            raise NotImplementedError("Нельзя создать такой объект")
    def link(self,nextEl, nextInd):
        self.__nextEl = nextEl
        self.__nextIn = nextInd
    @property
    def In1(self):
        return self.__in1
    @property
    def In2(self):
        return self.__in2

    @In1.setter
    def In1(self, newIn1 ):
        self.__in1 = newIn1
        self.calc()
        if self.__nextEl:
            if self.__nextIn == 1:
                self.__nextEl.In1 = self._res
            elif self.__nextIn == 2:
                self.__nextEl.In2 = self._res

    @In2.setter
    def In2(self, newIn2 ):
        self.__in2 = newIn2
        self.calc()
        if self.__nextEl:
            if self.__nextIn == 1:
                self.__nextEl.In1 = self._res
            elif self.__nextIn == 2:
                self.__nextEl.In2 = self._res


class Tlog2In(LogOperation):
    pass
class Tlog1In(LogOperation):
    pass
class TNot(Tlog1In):
    def __init__(self):
        super().__init__()
    def calc(self):
        self._res = not self.In1
class TAnd(Tlog2In):
    def __init__(self):
        super().__init__()
    def calc(self):
        self._res = self.In1 and self.In2
class TOr(Tlog2In):
    def __init__(self):
        super().__init__()
    def calc(self):
        self._res = self.In1 or self.In2

not1 = TNot()
not2 = TNot()
and1 = TAnd()
and2 = TAnd()
or1 = TOr()
not1.link(and1, 1)
not2.link(and2, 1)
and1.link(or1, 1)
and2.link(or1, 2)



print ( " A | B | Xor(A, B) " );
print ( "-------------------" );
for A in range(2):
    not1.In1 = bool(A)
    and2.In2 = bool(A)
    for B in range(2):
        not2.In1 = bool(B)
        and1.In2 = bool(B)
        print ( " ", A, "|", B, "|", int(or1._res) )