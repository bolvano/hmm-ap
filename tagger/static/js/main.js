$( document ).ready(function() {

if ($('#map').length) {
    ymaps.ready(initMap);
}

function initMap () {
    var myMap = new ymaps.Map('map', {
        center: [55.76, 37.64],
        zoom: 10,
        controls: ['zoomControl']
    }, {
        searchControlProvider: 'yandex#search'
    });

    var input = $('.address-input');

    myMap.events.add('click', function (e) {
        var coords = e.get('coords');

        // взять адрес с карты
        getAddress(coords, input);
    });

    // найти адрес на карте
    input.donetyping(function(){
      ymaps.geocode(input.val(), { results: 1 })
           .then(function(res) {

                var firstGeoObject = res.geoObjects.get(0),
                    coords = firstGeoObject.geometry.getCoordinates(),
                    bounds = firstGeoObject.properties.get('boundedBy');

                myMap.geoObjects.add(firstGeoObject);

                myMap.setBounds(bounds, {
                    checkZoomRange: true
                });
           });
    });
}

function getAddress(coords, input) {
    ymaps.geocode(coords).then(function (res) {
        input.val(res.geoObjects.get(0).properties.get('text').replace('Россия, ', ''));
    });
}

/* DONETYPING PLUGIN */
;(function($){
    $.fn.extend({
        donetyping: function(callback,timeout){
            timeout = timeout || 1e3; // 1 second default timeout
            var timeoutReference,
                doneTyping = function(el){
                    if (!timeoutReference) return;
                    timeoutReference = null;
                    callback.call(el);
                };
            return this.each(function(i,el){
                var $el = $(el);

                $el.is(':input') && $el.on('keyup keypress paste',function(e){
                    if (e.type=='keyup' && e.keyCode!=8) return;

                    if (timeoutReference) clearTimeout(timeoutReference);
                    timeoutReference = setTimeout(function(){
                        doneTyping(el);
                    }, timeout);
                }).on('blur',function() {
                    doneTyping(el);
                });
            });
        }
    });
})(jQuery);
});

