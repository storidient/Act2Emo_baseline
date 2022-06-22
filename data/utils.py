from attrs import define

@define
class Rx:
  target : str
  outcome : str
  level : int

@define
class B:
  open: str
  close : str

