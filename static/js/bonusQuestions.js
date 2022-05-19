// you receive an array of objects which you must sort in the by the key "sortField" in the "sortDirection"
function getSortedItems(items, sortField, sortDirection) {
    console.log(items)
    console.log(sortField)
    console.log(sortDirection)

    // === SAMPLE CODE ===
    // if you have not changed the original html uncomment the code below to have an idea of the
    // effect this function has on the table
    //
    if (sortDirection === "asc") {
        const firstItem = items.shift()
        if (firstItem) {
            items.push(firstItem)
        }
    } else {
        const lastItem = items.pop()
        if (lastItem) {
            items.push(lastItem)
        }
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
            if (!(items[j]['Title'].includes(filterValue.slice(1)) || items[j]['Description'].includes(filterValue.slice(1)))){
                filter_list.push(items[j])
            }
        } else if(items[j]['Title'].includes(filterValue) || items[j]['Description'].includes(filterValue)) {
            filter_list.push(items[j])
        }
    }
    return filter_list
}

function toggleTheme() {
    console.log("toggle theme")
}

function increaseFont() {
    console.log("increaseFont")
}

function decreaseFont() {
    console.log("decreaseFont")
}