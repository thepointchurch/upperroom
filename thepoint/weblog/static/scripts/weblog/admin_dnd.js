function get_md(row) {
    var slug = row.children(".field-slug").children("input").val().trim();
    var description = row.children(".field-description").children("textarea").val().trim();
    var prefix = "";
    var mime_type = "";
    try {
        mime_type = row.children(".field-file").find("input").get(0).files[0].type.split("/")[0];
    } catch(e) {
        mime_type = row.children(".field-mime_type").text().trim().split("/")[0];
    }
    if (row.children(".field-kind").children("select").val().trim() == "I" && mime_type == "image") {
        prefix = "!";
    }
    return prefix + "[" + description + "][" + slug + "]";
}

(function($) {
    $(function() {
        var attachment_drag_opts = {
            revert: true,
            helper: function() {
                return $("<div>" + get_md($(this).parent()) + "</div>");
            },
            cursor: "grabbing",
            opacity: 0.5,
        };

        $(".field-drag_handle").disableSelection();
        $(".field-drag_handle").not(".empty-form .field-drag_handle").draggable(attachment_drag_opts);
        $(document).on("formset:added", function(event, $row, formsetName) {
            if (formsetName == "attachments") {
                $row.find(".field-drag_handle").draggable(attachment_drag_opts);
            }
        });

        $("#id_body, #id_description").droppable({
            accept: ".field-drag_handle",
            activeClass: "dropping",
            over: function( event, ui ) {
                this.original_value = this.value;
                $(this).insert_at_caret(get_md(ui.draggable.parent()));
            },
            out: function( event, ui ) {
                this.value = this.original_value;
            },
        });

        $.fn.insert_at_caret = function (link_text) {
            return this.each(function(){
                if (this.selectionStart || this.selectionStart == "0") {
                    var start = this.selectionStart;
                    var end = this.selectionEnd;
                    var scroll_top = this.scrollTop;
                    this.value = this.value.substring(0, start) + link_text + this.value.substring(end, this.value.length);
                    this.focus();
                    this.selectionStart = start + link_text.length;
                    this.selectionEnd = start + link_text.length;
                    this.scrollTop = scroll_top;
                } else {
                    this.value += link_text;
                    this.focus();
                }
            });
        };
    });
})(django.jQuery);
