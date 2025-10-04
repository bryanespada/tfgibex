
// Redireccion de elementos del dom
function redirect(object) {
    var url = object.getAttribute('data-url');
    window.location.href = url;
}

// Funcion para filtrar los elementos de mercados y bolsas 
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

// Funcion para filtrar los elementos de empresas, noticias, mercados y bolsas
function filterBlock() {
    console.log("Cargado Filter Block");
    var filterValue = $('#filterInputBlock').val().toLowerCase();
    var noResultsMessage = document.getElementById("noResultsMessage");
    var anyResults = false;

    $('.blog').each(function () {
        // Buscar solo en el título
        var titleText = '';

        // Para tarjetas con título en h4 (mercados, bolsas, empresas nuevas)
        var h4Title = $(this).find('h4').first().text();
        if (h4Title) {
            titleText = h4Title.toLowerCase();
        }

        // Para tarjetas con título en b (noticias)
        var bTitle = $(this).find('.caption b').first().text();
        if (bTitle && !titleText) {
            titleText = bTitle.toLowerCase();
        }

        // Verificar si el título coincide con el filtro
        if (titleText.indexOf(filterValue) > -1) {
            anyResults = true;
            $(this).show();
        } else {
            $(this).hide();
        }
    });

    // Mostrar u ocultar mensaje de "no resultados"
    if (filterValue === '') {
        // Si no hay filtro, ocultar mensaje y mostrar todo
        noResultsMessage.classList.add('d-none');
        $('.blog').show();
    } else if (anyResults) {
        // Si hay resultados, ocultar mensaje
        noResultsMessage.classList.add('d-none');
    } else {
        // Si no hay resultados, mostrar mensaje
        noResultsMessage.classList.remove('d-none');
    }
}

// 
