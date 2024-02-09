const dateCanOpenPromise = fetchDateCanOpen()
let dateLeft;

main()
setInterval(main, 1000)

async function main() {
    dateLeft = calculateDateLeft(dateCanOpenPromise)
    const dateLeftObject = await dateLeft

    if (dateLeftIsZero(dateLeftObject)) {
        reloadPage()
    } else {
        updateDocumentDateLeft(dateLeftObject)
    }
}

function reloadPage() {
    location.reload()
}

function dateLeftIsZero(dateLeft) {
    for (const dateKey in dateLeft) {
        if (dateLeft[dateKey] !== 0) {
            return false
        }
    }

    alreadyReloadedPage = true
    return true
}

async function fetchDateCanOpen() {
    try {
        const response = await fetch('/' +
            `timegram_datetime_can_open/${getTimegramID()}`)

        if (response.ok) {
            const responseJson = await response.json()
            return responseJson
        } else {
            throw new Error('Deu errado, parceiro')
        }
    } catch (error) {
        console.error(error)
    }
}

function getTimegramID() {
    let currentUrl = window.location.href;

    if (currentUrl.at(-1) === '/') {
        currentUrl = currentUrl.substring(0, currentUrl.length - 1)
    }

    let lastIndexOfBar = currentUrl.lastIndexOf('/')
    let ID = currentUrl.substring(lastIndexOfBar + 1, currentUrl.length)

    return ID
}

async function calculateDateLeft(dateCanOpenPromise) {
    try {
        const currentDateUTC = getCurrentDateUTC()

        const dateCanOpenObject = await dateCanOpenPromise
        const dateCanOpen = objectToDate(dateCanOpenObject)

        return subtractDates(dateCanOpen, currentDateUTC)

    } catch (error) {
        console.error(error)
    }
}

function getCurrentDateUTC() {
    const SECONDS_IN_A_MINUTE = 60
    const MILLISECONDS_IN_A_SECOND = 1000

    const currentDateLocal = new Date()
    const currentDateMilliseconds = currentDateLocal.getTime()
    const timezoneOffsetMilliseconds =
        currentDateLocal.getTimezoneOffset() * SECONDS_IN_A_MINUTE * MILLISECONDS_IN_A_SECOND

    let currentDateUTC = new Date()
    currentDateUTC.setTime(currentDateMilliseconds + timezoneOffsetMilliseconds)

    return currentDateUTC
}

function objectToDate(object) {
    return new Date(object.year, object.month - 1, object.day, object.hour, object.minute, object.second)
}

function dateToObject(date) {
    return {
        'year': date.getUTCFullYear(),
        'month': date.getUTCMonth(),
        'day': date.getUTCDate(),
        'hour': date.getUTCHours(),
        'minute': date.getUTCMinutes(),
        'second': date.getUTCSeconds(),
    }
}

function subtractDates(dateA, dateB) {
    const MONTHS_IN_A_YEAR = 12

    const DAYS_IN_A_MONTH =
        [31, {false: 28, true: 29}, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

    const HOURS_IN_A_DAY = 24
    const MINUTES_IN_A_HOUR = 60
    const SECONDS_IN_A_MINUTE = 60

    const DATE_CONVERSIONS = {
        'year': undefined,
        'month': MONTHS_IN_A_YEAR,
        'day': DAYS_IN_A_MONTH,
        'hour': HOURS_IN_A_DAY,
        'minute': MINUTES_IN_A_HOUR,
        'second': SECONDS_IN_A_MINUTE
    }

    let dateOffsets = {}

    let dateObjectA = dateToObject(dateA)
    let dateObjectB = dateToObject(dateB)

    const dateKeys = ['second', 'minute', 'hour', 'day', 'month', 'year']

    if (dateB > dateA) {
        for (const dateKey in dateKeys) {
            dateOffsets[dateKey] = 0
        }

        return dateOffsets
    }


    for (let i = 0; i < dateKeys.length; i++) {
        const dateKey = dateKeys[i]
        let dateOffset = dateObjectA[dateKey] - dateObjectB[dateKey]

        if (dateOffset < 0) {

            if (DATE_CONVERSIONS[dateKey] instanceof Object) {
                dateOffset += DATE_CONVERSIONS[dateKey][1][isLeapYear(dateObjectA.year)]
            } else {
                dateOffset += DATE_CONVERSIONS[dateKey]
            }

            const nextDateKey = dateKeys[i + 1]
            dateObjectA[nextDateKey] -= 1
        }

        dateOffsets[dateKey] = dateOffset
    }

    return dateOffsets
}

function isLeapYear(year) {
    return year % 4 === 0
}

function updateDocumentDateLeft(dateLeft) {
    const IDGroups = {
        'year': {
            'element': 'years-left',
            'elementLabel': 'years-left-label'
        },
        'month': {
            'element': 'months-left',
            'elementLabel': 'months-left-label'
        },
        'day': {
            'element': 'days-left',
            'elementLabel': 'days-left-label'
        },
        'hour': {
            'element': 'hours-left',
            'elementLabel': undefined
        },
        'minute': {
            'element': 'minutes-left',
            'elementLabel': undefined
        },
        'second': {
            'element': 'seconds-left',
            'elementLabel': undefined
        },
    }

    const elementLabelsContent = {
        'year': {
            false: 'ano',
            true: 'anos',
        },
        'month': {
            false: 'mês',
            true: 'meses',
        },
        'day': {
            false: 'dia',
            true: 'dias',
        }
    }

    for (const dateKey in IDGroups) {
        const element =
            document.getElementById(IDGroups[dateKey].element)
        element.textContent = dateLeft[dateKey]

        if (IDGroups[dateKey].elementLabel !== undefined) {
            const elementLabel =
                document.getElementById(IDGroups[dateKey].elementLabel)
            elementLabel.textContent = elementLabelsContent[dateKey][dateLeft[dateKey] !== 1]
        }
    }
}






