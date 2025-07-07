const carData = {
    "Toyota": {
        "models": ["Camry", "Corolla", "RAV4", "Highlander", "Prius"],
        "years": Array.from({length: 10}, (_, i) => new Date().getFullYear() - i)
    },
    "Honda": {
        "models": ["Civic", "Accord", "CR-V", "Pilot", "HR-V"],
        "years": Array.from({length: 10}, (_, i) => new Date().getFullYear() - i)
    },
    "BMW": {
        "models": ["3 Series", "5 Series", "X3", "X5", "7 Series"],
        "years": Array.from({length: 10}, (_, i) => new Date().getFullYear() - i)
    },
    "Mercedes": {
        "models": ["C-Class", "E-Class", "GLC", "GLE", "S-Class"],
        "years": Array.from({length: 10}, (_, i) => new Date().getFullYear() - i)
    }
};
