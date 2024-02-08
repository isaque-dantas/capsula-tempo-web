const dataLabels = document.getElementsByClassName("data-label")

let widths = []
for (let i=0; i<dataLabels.length; i++) {
    widths.push(dataLabels[i].getBoundingClientRect().width)
}

const longestWidth = widths.reduce(
    (a, b) => Math.max(a, b), -Infinity
)

for (let i=0; i<dataLabels.length; i++) {
    dataLabels[i].style.width = `${longestWidth + 24}px`
}
