const themeOptions = {
    palette: {
        mode: 'dark',
        primary: {
            main: '#0f0',
            dark: '#003D00',
            light: '#ccffbe',
            contrastText: '#212121',
        },
        background: {
            default: '#333135',
            paper: '#212121',
        },
        secondary: {
            main: '#c000ff',
            dark: '#45008D',
            light: '#eabafe',
            contrastText: '#212121',
        },
    },
    typography: {
        fontFamily: 'Ubuntu Mono, Open Sans',
        h1: {
            fontFamily: 'Ubuntu Mono',
        },
        h2: {
            fontFamily: 'Ubuntu Mono',
        },
        h3: {
            fontFamily: 'Ubuntu Mono',
        },
        h4: {
            fontFamily: 'Ubuntu Mono',
        },
        h6: {
            fontFamily: 'Ubuntu Mono',
        },
        h5: {
            fontFamily: 'Ubuntu Mono',
        },
        subtitle1: {
            fontFamily: 'Ubuntu Mono',
        },
        subtitle2: {
            fontFamily: 'Ubuntu Mono',
        },
        button: {
            fontFamily: 'Ubuntu Mono',
            fontSize: '1rem',
            // fontWeight: 700,
            // lineHeight: 1.75,
            justifyContent: 'flex-start',
            textTransform: 'none',
        },
        overline: {
            fontFamily: 'Ubuntu Mono',
        },
        input: {
            fontFamily: 'Ubuntu Mono',
        },
    },
    // components: {
    //     MuiOutlinedInput: {
    //         variants: [
    //             // variants will help you define the props given by Mui and the styles you want to apply for it
    //             {
    //                 props: { disabled: true },
    //                 style: {
    //                     // backgroundColor: 'green',
    //                     color: 'rgb(0,0,0,0.5)',
    //                     // fontSize: '5rem',
    //                 },
    //             },
    //         ],
    //     },
    // },
    props: {
        MuiButton: {
            size: 'small',
        },
        MuiButtonGroup: {
            size: 'small',
        },
        MuiCheckbox: {
            size: 'small',
        },
        MuiFab: {
            size: 'small',
        },
        MuiFormControl: {
            margin: 'dense',
            size: 'small',
        },
        MuiFormHelperText: {
            margin: 'dense',
        },
        MuiIconButton: {
            size: 'small',
        },
        MuiInputBase: {
            margin: 'dense',
            // fontFamily: 'Ubuntu Mono',
        },
        MuiInputLabel: {
            margin: 'dense',
        },
        MuiRadio: {
            size: 'small',
        },
        MuiSwitch: {
            size: 'small',
        },
        MuiTextField: {
            margin: 'dense',
            size: 'small',
        },
        MuiOutlinedInput: {
            margin: 'dense',
        },
    },
    shape: {
        borderRadius: 0,
    },
    spacing: 8,
};

export default themeOptions;
