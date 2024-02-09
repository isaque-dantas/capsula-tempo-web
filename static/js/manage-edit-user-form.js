const textInputs = getTextInputs()
const labels = document.getElementsByTagName("label")
const formButtonContainer = document.getElementById("form-button-container")

const initialLabelsForProperties = getLabelsForProperties(labels)

unableForm()
formButtonContainer.style.visibility = 'visible'

function getTextInputs() {
    const inputs = document.getElementsByTagName("input")
    let textInputs = []

    for (let i=0; i<inputs.length; i++) {
        if (inputs[i].type === "text" || inputs[i].type === "email" ) {
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

function unableForm() {
    hideFormButtons()
    changeInputsReadOnlyPropertyTo(true)
    removeLabelsForProperties()
}

function enableForm() {
    showFormButtons()
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
        labels[i].htmlFor = initialLabelsForProperties[i]
    }
}

function hideFormButtons() {
    formButtonContainer.style.width = "0px"
}

function showFormButtons() {
    formButtonContainer.style.width = "100%"
}
