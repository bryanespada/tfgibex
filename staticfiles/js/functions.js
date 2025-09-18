
// Redireccion de elementos del dom
function redirect(object) {
    var url = object.getAttribute('data-url');
    window.location.href = url;
}

// Funcion para filtrar los elementos de surgical areas y surgery types 
function filterTable() {
    var input, filter, table, tr, td, i, txtValue, noResultsMessage;
    input = document.getElementById("filterInput");
    filter = input.value.toUpperCase();
    table = document.getElementById("mytable");
    noResultsMessage = document.getElementById("noResultsMessage");
    tr = table.getElementsByTagName("tr");

    var found = false; 
    for (i = 0; i < tr.length; i++) {
        // Obtener la segunda celda (índice 1) de la fila
        td = tr[i].getElementsByTagName("td")[1];
        if (td) {
            // Obtener el texto de la segunda celda
            txtValue = td.textContent || td.innerText;
            // Convertir a mayúsculas para hacer la búsqueda insensible a mayúsculas y minúsculas
            txtValueUpperCase = txtValue.toUpperCase();
            // Verificar si el texto de la segunda celda coincide con el filtro
            if (txtValueUpperCase.indexOf(filter) > -1) {
                // Mostrar la fila si coincide
                tr[i].style.display = "";
                found = true;
            } else {
                // Ocultar la fila si no coincide
                tr[i].style.display = "none";
            }
        }
    }
    // Mostrar o ocultar el mensaje de "No hay resultados" según si se encontraron resultados o no
    if (found) {
        table.classList.remove('d-none');
        noResultsMessage.classList.add('d-none'); 
    } else {
        table.classList.add('d-none');
        noResultsMessage.classList.remove('d-none');
    }
}

// Funcion para filtrar los elementos de peripheral blocks
function filterBlock() {
    console.log("Cargado Filter Block")
    var filterValue = $('#filterInputBlock').val().toLowerCase();
    noResultsMessage = document.getElementById("noResultsMessage");
    var anyResults = false;
    $('.blog').each(function () {
        var textToFilter = $(this).find('.caption p').text().toLowerCase();
        if (textToFilter.indexOf(filterValue) > -1) {
            anyresult = true;
            $(this).show();
        } else {
            $(this).hide();
        }
    });
    if (anyResults) {
        noResultsMessage.classList.remove('d-none');
    }
    else if (filterValue == ''){
        noResultsMessage.classList.add('d-none');
    }
    else {
        noResultsMessage.classList.add('d-none'); 
    }
}

// 
