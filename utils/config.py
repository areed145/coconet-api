from matplotlib import cm
from matplotlib.colors import (
    ListedColormap,
    LinearSegmentedColormap,
    rgb2hex,
    to_rgba,
)

oilgas_params = {
    "oil": {"color": "#50bf37"},
    "water": {"color": "#4286f4"},
    "gas": {"color": "#ef2626"},
    "steam": {"color": "#e32980"},
    "cyclic": {"color": "#fcd555"},
    "water_inj": {"color": "#03b6fc"},
    "gasair_inj": {"color": "#fc7703"},
    "oilgrav": {"color": "#81d636"},
    "pcsg": {"color": "#4136d6"},
    "ptbg": {"color": "#7636d6"},
    "btu": {"color": "#d636d1"},
    "pinjsurf": {"color": "#e38f29"},
}

wx_params = {
    "flight_category": {
        "min": 0,
        "max": 0,
        "mult": 0,
        "shift": 0,
        "unit": "",
        "colorscale": {
            "vfr": "rgb(0,255,0)",
            "mvfr": "rgb(0,0,255)",
            "ifr": "rgb(255,0,0)",
            "lifr": "rgb(255,127.5,255)",
        },
    },
    "temp_c": {
        "min": 0,
        "max": 100,
        "mult": 1.8,
        "shift": 32,
        "unit": "F",
        "color": "",
    },
    "temp_c_var": {
        "min": 0,
        "max": 100,
        "mult": 1.8,
        "shift": 0,
        "unit": "F",
        "color": "",
    },
    "temp_c_delta": {
        "min": 0,
        "max": 100,
        "mult": 1.8,
        "shift": 0,
        "unit": "F",
        "color": "",
    },
    "dewpoint_c": {
        "min": 0,
        "max": 100,
        "mult": 1.8,
        "shift": 32,
        "unit": "F",
        "color": "",
    },
    "dewpoint_c_delta": {
        "min": 0,
        "max": 100,
        "mult": 1.8,
        "shift": 0,
        "unit": "F",
        "color": "",
    },
    "temp_dewpoint_spread": {
        "min": 0,
        "max": 100,
        "mult": 1.8,
        "shift": 0,
        "unit": "F",
        "color": "",
    },
    "altim_in_hg": {
        "min": 28,
        "max": 34,
        "mult": 1,
        "shift": 0,
        "unit": "inHg",
        "color": "",
    },
    "altim_in_hg_var": {
        "min": 0,
        "max": 10,
        "mult": 1,
        "shift": 0,
        "unit": "inHg",
        "color": "",
    },
    "altim_in_hg_delta": {
        "min": 0,
        "max": 10,
        "mult": 1,
        "shift": 0,
        "unit": "inHg",
        "color": "",
    },
    "wind_dir_degrees": {
        "min": 0,
        "max": 359,
        "mult": 1,
        "shift": 0,
        "unit": "degrees",
        "color": "",
    },
    "wind_speed_kt": {
        "min": 0,
        "max": 100,
        "mult": 1,
        "shift": 0,
        "unit": "kts",
        "color": "",
    },
    "wind_speed_kt_delta": {
        "min": 0,
        "max": 100,
        "mult": 1,
        "shift": 0,
        "unit": "kts",
        "color": "",
    },
    "wind_gust_kt": {
        "min": 0,
        "max": 100,
        "mult": 1,
        "shift": 0,
        "unit": "kts",
        "color": "",
    },
    "wind_gust_kt_delta": {
        "min": 0,
        "max": 100,
        "mult": 1,
        "shift": 0,
        "unit": "kts",
        "color": "",
    },
    "visibility_statute_mi": {
        "min": 0,
        "max": 100,
        "mult": 1,
        "shift": 0,
        "unit": "mi",
        "color": "",
    },
    "cloud_base_ft_agl_0": {
        "min": 0,
        "max": 10000,
        "mult": 1,
        "shift": 0,
        "unit": "ft",
        "color": "",
    },
    "cloud_base_ft_agl_0_delta": {
        "min": 0,
        "max": 10000,
        "mult": 1,
        "shift": 0,
        "unit": "ft",
        "color": "",
    },
    "sky_cover_0": {
        "min": 0,
        "max": 100,
        "mult": 1,
        "shift": 0,
        "unit": "degrees",
        "colorscale": {
            "clr": "rgb(21, 230, 234)",
            "few": "rgb(194, 234, 21)",
            "sct": "rgb(234, 216, 21)",
            "bkn": "rgb(234, 181, 21)",
            "ovc": "rgb(234, 77, 21)",
            "ovx": "rgb(234, 21, 21)",
        },
    },
    "precip_in": {
        "min": 0,
        "max": 10,
        "mult": 1,
        "shift": 0,
        "unit": "degrees",
        "color": "",
    },
    "elevation_m": {
        "min": 0,
        "max": 10000,
        "mult": 3.2808,
        "shift": 0,
        "unit": "ft",
        "color": "",
    },
    "age": {
        "min": 0,
        "max": 90,
        "mult": 1,
        "shift": 0,
        "unit": "minutes",
        "color": "",
    },
    "three_hr_pressure_tendency_mb": {
        "min": 0,
        "max": 10000,
        "mult": 1,
        "shift": 0,
        "unit": "?",
        "color": "",
    },
}

colorway = [
    "#b8fb3c",
    "#5ce5d5",
    "#fe53bb",
    "#7898fb",
    # '#001437',
    "#09fbd3",
    "#f5d300",
    "#3cb9fc",
    "#b537f2",
    "#8a2be2",
    # '#120052',
    "#08f7fe",
    "#09fbd3",
    "#fe53bb",
]

cs_normal = [
    [0.0, "#424ded"],
    [0.1, "#4283ed"],
    [0.2, "#42d0ed"],
    [0.3, "#42edae"],
    [0.4, "#78ed42"],
    [0.5, "#d6ed42"],
    [0.6, "#edde42"],
    [0.7, "#f4af41"],
    [0.8, "#f48541"],
    [0.9, "#f44741"],
    [1.0, "#f44298"],
]

cs_rdgn = [
    [0.0, "#f44741"],
    [0.2, "#f48541"],
    [0.4, "#f4af41"],
    [0.6, "#edde42"],
    [0.8, "#d6ed42"],
    [1.0, "#78ed42"],
]

cs_gnrd = [
    [0.0, "#78ed42"],
    [0.2, "#d6ed42"],
    [0.4, "#edde42"],
    [0.6, "#f4af41"],
    [0.8, "#f48541"],
    [1.0, "#f44741"],
]

cs_crm = [
    [0.0, "#21d411"],
    [0.4, "#21d411"],
    [0.45, "#f7e926"],
    [0.475, "#f67513"],
    [0.525, "#ed0c0c"],
    [0.55, "#f613e7"],
    [1.0, "#f613e7"],
]

cs_circle = [
    [0.000, "#f45f42"],
    [0.067, "#f7856f"],
    [0.133, "#e2aba1"],
    [0.200, "#d8bdb8"],
    [0.267, "#BCBCBC"],
    [0.333, "#bac8e0"],
    [0.400, "#aeccfc"],
    [0.467, "#77aaf9"],
    [0.533, "#4186f4"],
    [0.600, "#77aaf9"],
    [0.667, "#aeccfc"],
    [0.733, "#bac8e0"],
    [0.800, "#BCBCBC"],
    [0.867, "#d8bdb8"],
    [0.933, "#e2aba1"],
    [1.000, "#f7856f"],
]

cs_updown = [
    [0.000, "#4186f4"],
    [0.125, "#77aaf9"],
    [0.250, "#aeccfc"],
    [0.375, "#bac8e0"],
    [0.500, "#BCBCBC"],
    [0.625, "#d8bdb8"],
    [0.750, "#e2aba1"],
    [0.875, "#f7856f"],
    [1.000, "#f45f42"],
]

cs_circle = [
    [0.000, "#ff4336"],
    [0.067, "#ff7936"],
    [0.133, "#ffaf36"],
    [0.200, "#ffc636"],
    [0.267, "#ffee36"],
    [0.333, "#d0ff36"],
    [0.400, "#a5ff36"],
    [0.467, "#72ff36"],
    [0.533, "#36ff43"],
    [0.600, "#36ffa5"],
    [0.667, "#36ffff"],
    [0.733, "#36d0ff"],
    [0.800, "#368aff"],
    [0.867, "#bf36ff"],
    [0.933, "#ff36c6"],
    [1.000, "#ff3665"],
]

scl_oil = [
    [0.00, "#d6ed42"],
    [0.10, "#78ed42"],
    [0.50, "#50bf37"],
    [1.00, "#06721e"],
]

scl_oil_log = [
    [0, "#dbdbdb"],  # 0
    [1.0 / 1000, "#d6ed42"],  # 10
    [1.0 / 100, "#78ed42"],  # 100
    [1.0 / 10, "#50bf37"],  # 1000
    [1.0, "#06721e"],  # 10000
]

scl_wtr = [
    [0.00, "#caf0f7"],
    [0.33, "#64d6ea"],
    [0.66, "#4286f4"],
    [1.00, "#0255db"],
]

scl_wtr_log = [
    [0, "#dbdbdb"],  # 0
    [1.0 / 1000, "#caf0f7"],  # 10
    [1.0 / 100, "#64d6ea"],  # 100
    [1.0 / 10, "#4286f4"],  # 1000
    [1.0, "#0255db"],  # 10000
]

scl_gas = [
    [0.00, "#fcbfbf"],
    [0.33, "#f28282"],
    [0.66, "#ef2626"],
    [1.00, "#7a0707"],
]

scl_stm = [
    [0.00, "#edb6d7"],
    [0.33, "#ed87c4"],
    [0.66, "#e22f9b"],
    [1.00, "#930b5d"],
]

scl_stm_log = [
    [0, "#dbdbdb"],  # 0
    [1.0 / 1000, "#edb6d7"],  # 10
    [1.0 / 100, "#ed87c4"],  # 100
    [1.0 / 10, "#e22f9b"],  # 1000
    [1.0, "#930b5d"],  # 10000
]

scl_cyc = [
    [0.00, "#fff1c6"],
    [0.33, "#f7dd8a"],
    [0.66, "#fcd555"],
    [1.00, "#ffc300"],
]


def time_cm(total):
    c0 = np.array([245 / 256, 200 / 256, 66 / 256, 1])
    c1 = np.array([245 / 256, 218 / 256, 66 / 256, 1])
    c2 = np.array([188 / 256, 245 / 256, 66 / 256, 1])
    c3 = np.array([108 / 256, 201 / 256, 46 / 256, 1])
    c4 = np.array([82 / 256, 138 / 256, 45 / 256, 1])
    c5 = np.array([24 / 256, 110 / 256, 45 / 256, 1])
    cm = LinearSegmentedColormap.from_list(
        "custom", [c0, c1, c2, c3, c4, c5], N=total
    )
    return cm
