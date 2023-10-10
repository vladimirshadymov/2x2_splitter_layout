import gdsfactory as gf
import numpy as np

chip = gf.Component()

bare_chip = gf.components.die(
    size=(5200, 5200),  # Size of die
    street_width=100,  # Width of corner marks for die-sawing
    street_length=1000,  # Length of corner marks for die-sawing
    die_name="chip99",  # Label text
    text_size=100,  # Label text size
    text_location="SW",  # Label text compass location e.g. 'S', 'SE', 'SW'
    layer=(2, 0),
    bbox_layer=(3, 0),
)

chip.add_ref(bare_chip)
EDGE_COUPLER_LENGTH = 150
EDGE_COUPLER_HANGOUT = 100
edge_coupler_si = gf.components.edge_coupler_silicon(length=EDGE_COUPLER_LENGTH, width1=0.5, width2=0.2, with_bbox=True, with_two_ports=True, cross_section='xs_sc', port_order_name=['o1', 'o2'], port_order_types=['optical', 'optical'], add_pins=True)
edge_coupler_si = gf.components.extend_ports(edge_coupler_si, port_names=['o2'], length=EDGE_COUPLER_HANGOUT, port_type='optical', centered=False)
right_edge_couplers = gf.components.edge_coupler_array(edge_coupler=edge_coupler_si, n=38, pitch=127.0, x_reflection=False, text_offset=[10, 20], text_rotation=0)
right = chip.add_ref(right_edge_couplers)
right.move([2500-EDGE_COUPLER_LENGTH-EDGE_COUPLER_HANGOUT/2, -127*38/2+90])

left_edge_couplers = gf.components.edge_coupler_array(edge_coupler=edge_coupler_si, n=38, pitch=127.0, x_reflection=True, text_offset=[-130, 20], text_rotation=0)
left = chip.add_ref(left_edge_couplers)
left.move([-2500+EDGE_COUPLER_LENGTH+EDGE_COUPLER_HANGOUT/2, -127*38/2+90])


directional_coupler_lengths = np.linspace(10, 200, 19)
COUPLING_GAP = 0.3

for (idx, len) in enumerate(directional_coupler_lengths):
    splitter = gf.components.coupler(gap=COUPLING_GAP, length=len, dy=4.0, dx=10.0, cross_section='xs_sc')
    splitter_ref_tmp = chip.add_ref(splitter)
    splitter_ref_tmp.move([0, -127*38/2 + 127/2 + 90 + 127*2*idx])

    route = gf.routing.get_route(left.ports[f'o{76-idx*2}'], splitter_ref_tmp.ports['o1'])    
    chip.add(route.references) 

    route = gf.routing.get_route(left.ports[f'o{76-idx*2-1}'], splitter_ref_tmp.ports['o2'])    
    chip.add(route.references) 

    route = gf.routing.get_route(right.ports[f'o{idx*2+1}'], splitter_ref_tmp.ports['o4'])    
    chip.add(route.references) 

    route = gf.routing.get_route(right.ports[f'o{idx*2+2}'], splitter_ref_tmp.ports['o3'])    
    chip.add(route.references) 

chip.write_gds('chip.gds')