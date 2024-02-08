const textInputs = getTextInputs()
const buttons = document.getElementsByClassName("form-button")
console.log(buttons)
const labels = document.getElementsByTagName("label")

const originalLabelsForProperties = getLabelsForProperties(labels)

function getTextInputs() {
    const inputs = document.getElementsByTagName("input")
    let textInputs = []

    for (let i=0; i<inputs.length; i++) {
        if (inputs[i].type === "text" ) {
            textInputs.push(inputs[i])
        }
    }

    return textInputs
}

function getLabelsForProperties() {
    let forProperties = []

    for (let i = 0; i < labels.length; i++) {
        forProperties.push(labels[i].htmlFor)
    }

    return forProperties
}

unableForm()

function unableForm() {
    changeInputsReadOnlyPropertyTo(true)
    removeLabelsForProperties()
}

function enableForm() {
    changeInputsReadOnlyPropertyTo(false)
    restoreOriginalLabelsForProperties()
}

function changeInputsReadOnlyPropertyTo(readOnlyProperty) {
    for (let i = 0; i < textInputs.length; i++) {
        textInputs[i].readOnly = readOnlyProperty
    }
}

function removeLabelsForProperties() {
    for (let i = 0; i < labels.length; i++) {
        labels[i].htmlFor = ""
    }
}

function restoreOriginalLabelsForProperties() {
    for (let i = 0; i < labels.length; i++) {
        labels[i].htmlFor = originalLabelsForProperties[i]
    }
}

