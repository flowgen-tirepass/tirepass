/**
 * 브랜드 선택 시 패턴 필터링
 * 브랜드를 선택하면 해당 브랜드의 패턴만 표시 (API로 동적 로드)
 */
window.addEventListener('load', function() {
    'use strict';

    // Django admin jQuery 사용
    if (typeof django === 'undefined' || typeof django.jQuery === 'undefined') {
        console.error('Django jQuery not loaded');
        return;
    }

    var $ = django.jQuery;

    $(document).ready(function() {
        var $brandField = $('#id_brand');
        var $patternField = $('#id_pattern');

        if ($brandField.length && $patternField.length) {
            // 브랜드 선택 변경 시
            $brandField.on('change', function() {
                var selectedBrandId = $(this).val();

                // 패턴 필드 초기화
                $patternField.empty();
                $patternField.append('<option value="">---------</option>');

                if (selectedBrandId) {
                    // JSON API로 선택된 브랜드의 패턴 가져오기
                    var apiUrl = '/admin/tire_data/brandpattern/?brand__id__exact=' + selectedBrandId + '&format=json';

                    $.ajax({
                        url: apiUrl,
                        dataType: 'json',
                        success: function(patterns) {
                            if (patterns && patterns.length > 0) {
                                patterns.forEach(function(pattern) {
                                    $patternField.append(
                                        $('<option></option>')
                                            .val(pattern.id)
                                            .text(pattern.pattern_name)
                                    );
                                });
                            }
                        },
                        error: function(xhr, status, error) {
                            // JSON API 없음 - HTML 페이지에서 파싱
                            $.get('/admin/tire_data/brandpattern/?brand__id__exact=' + selectedBrandId, function(html) {
                                var $html = $('<div>').html(html);
                                var $rows = $html.find('#result_list tbody tr');

                                $rows.each(function() {
                                    var $row = $(this);
                                    var patternId = $row.find('input[name="_selected_action"]').val();
                                    var patternName = $row.find('.field-pattern_name').text().trim();

                                    if (patternId && patternName) {
                                        $patternField.append(
                                            $('<option></option>')
                                                .val(patternId)
                                                .text(patternName)
                                        );
                                    }
                                });
                            });
                        }
                    });
                }
            });

            // 페이지 로드 시 이미 선택된 브랜드가 있으면 패턴 필터링
            if ($brandField.val()) {
                $brandField.trigger('change');
            }
        }
    });
});
