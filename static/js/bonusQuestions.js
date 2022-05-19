// you receive an array of objects which you must sort in the by the key "sortField" in the "sortDirection"
function getSortedItems(items, sortField, sortDirection) {
    function compare(a, b) {
        let elementA = isNaN(a[sortField]) ? a[sortField] : Number(a[sortField]);
        let elementB = isNaN(b[sortField]) ? b[sortField] : Number(b[sortField]);
        if (elementA < elementB) {
            return -1;
        }
        if (elementA > elementB) {
            return 1;
        }
        return 0;
    }

    console.log(items)
    console.log(sortField)
    console.log(sortDirection)

    // === SAMPLE CODE ===
    // if you have not changed the original html uncomment the code below to have an idea of the
    // effect this function has on the table
    //
    if (sortDirection === "asc") {
        items.sort(compare);
    } else {
        items.sort(compare);
        items.reverse();
    }

    return items
}

function getFilteredItems(items, filterValue) {
    let filter_list = [];
    for (let j = 0; j < items.length; j++) {
        if (filterValue.startsWith('Description:')) {
            if (items[j]['Description'].includes(filterValue.slice(12))) {
                filter_list.push(items[j])
            }
        } else if (filterValue.startsWith('!Description:')) {
            if (!items[j]['Description'].includes(filterValue.slice(13))) {
                filter_list.push(items[j])
            }
        } else if (filterValue.startsWith('!')) {
            if (!(items[j]['Title'].includes(filterValue.slice(1)) || items[j]['Description'].includes(filterValue.slice(1)))) {
                filter_list.push(items[j])
            }
        } else if (items[j]['Title'].includes(filterValue) || items[j]['Description'].includes(filterValue)) {
            filter_list.push(items[j])
        }
    }
    return filter_list
}

function increaseFont() {
    console.log("increaseFont");
    let bonusTable = document.querySelector('.bonus-table');
    let bonusTableStyles = getComputedStyle(bonusTable)
    let scale = Number(bonusTableStyles.getPropertyValue('--scale'))
    if (scale < 15) {
        bonusTable.style.setProperty('--scale', String(scale + 1));
    }
}

function decreaseFont() {
    console.log("decreaseFont")
    let bonusTable = document.querySelector('.bonus-table');
    let bonusTableStyles = getComputedStyle(bonusTable)
    let scale = Number(bonusTableStyles.getPropertyValue('--scale'))
    if (scale > 5) {
        bonusTable.style.setProperty('--scale', String(scale - 1));
    }
}
