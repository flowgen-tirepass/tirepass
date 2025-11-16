/**
 * 브랜드 선택 시 패턴 필터링
 * 브랜드를 선택하면 해당 브랜드의 패턴만 표시 (AJAX로 동적 로드)
 */
(function() {
    'use strict';

    // Django admin jQuery 사용
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
                    // AJAX로 선택된 브랜드의 패턴 가져오기
                    $.ajax({
                        url: '/admin/tire_data/customerbranddiscount/add/',
                        data: {
                            'brand': selectedBrandId
                        },
                        success: function(data) {
                            // 응답 HTML에서 pattern select 옵션 추출
                            var $tempDiv = $('<div>').html(data);
                            var $newPatternOptions = $tempDiv.find('#id_pattern option');

                            if ($newPatternOptions.length > 0) {
                                $newPatternOptions.each(function() {
                                    $patternField.append($(this).clone());
                                });
                            }
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
})();
