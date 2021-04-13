from schc_base import Tile
from schc_messages import RegularSCHCFragment
from schc_protocols import LoRaWAN

CONTENT = b"Hello World"


if __name__ == "__main__":
    schc_message = RegularSCHCFragment(
        rule_id=LoRaWAN.UPLINK,
        fcn=62,
        protocol=LoRaWAN().id,
        w=0
    )
    schc_message.add_tile(Tile(
        CONTENT
    ))
    schc_message.add_padding()
    with open("schc_fragment", "wb") as file:
        file.write(schc_message.as_bytes())
    print(schc_message.as_text())
