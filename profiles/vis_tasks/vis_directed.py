options = {
    "nodes": {
        "font": {
            "color": "rgb(0,0,0)"
        }
    },
    "edges": {
        "smooth": False,
        "arrows": {
            "to": {
                "enabled": True,
                "scaleFactor": 1,
                "type": "arrow"
            }
        },
        "color": {
            "color": "rgb(0,0,0)",
            "opacity": 0.5
        }
    },
    "physics": {
        "enabled": True,
        "barnesHut": {
            "avoidOverlap": 1,
            "centralGravity": 3.5
        },
        "maxVelocity": 1,
        "minVelocity": 1
    }
}


def node_json(n):
    return {"id": n, "label": n,
            "color": {"border": 'rgb(0,0,0)', "background": 'rgb(50,205,50)'},
            "font": {"color": 'rgb(0,0,0)'}}
