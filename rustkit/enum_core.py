from __future__ import annotations
import typing as t


def enum(cls: t.Type) -> t.Type:
    print(cls.__annotations__)

    for field, type in cls.__annotations__.items():
        type: str
        match type:
            case type if type == "...":
                # this is the simples one so far,
                # we need minimal attention here
                setattr(cls, field, ...)
                print(f"single attribute: {field} - {type}")
            case struct if type.startswith("{") and type.endswith("}"):
                # extract the fields
                struct_fields = {
                    field: type
                    for field, type in map(
                        lambda fields_set: fields_set.split(":"),
                        struct.replace(" ", "")[1:-1].split(",")
                    )
                }
                print(f"struct field: {field} - {struct_fields}")
            case tuple if type.startswith("(") and type.endswith(")"):
                # add type checks to the generated type.
                tuple_fields = [
                    type
                    for type in tuple.replace(" ", "")[1:-1].split(",")
                ]
                print(f"tuple field: {field} - {tuple_fields}")
            case type:
                # signle typed field, add a check to
                # see if the inserted data matches the types
                print(f"signle type {field} - {type}")

    return cls


@enum
class Enum:
    Quit: ...
    Move: {x: int, y: int}
    Write: str
    ChangeColor: (int, int, int)


if __name__ == '__main__':
    # Ok()
    # Err()
    pass
