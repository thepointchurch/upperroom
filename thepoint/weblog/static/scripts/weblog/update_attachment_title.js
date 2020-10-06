(function($) {
    $('input[id^="id_attachments-"][id$="-file"]').change(function() {
        var title_field = $('#' + this.id.replace(/-file$/, '-title'));
        title_field.val(this.value.split(/[\\\/]/).pop().replace(/\.[^/.]+$/, ''));
        title_field.trigger('change');
    });
})(django.jQuery);
