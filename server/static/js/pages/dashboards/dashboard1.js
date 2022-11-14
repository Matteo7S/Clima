/*
Template Name: Admin Pro Admin
Author: Wrappixel
Email: niravjoshi87@gmail.com
File: js
*/
$(function () {
    "use strict";
    // ============================================================== 
    // Newsletter
    // ============================================================== 

    //ct-visits
    new Chartist.Line('#ct-visits', {
        labels: ['2008', '2009', '2010', '2011', '2012', '2013', '2014', '2015'],
        series: [
            [5, 2, 7, 4, 5, 3, 5, 4]
            , [2, 5, 2, 6, 2, 5, 2, 4],
            [7, 7, 7, 10, 5, 2, 1, 1]
        ]
    }, {
        top: 0,
        low: 1,
        showPoint: true,
        fullWidth: true,
        plugins: [
            Chartist.plugins.tooltip()
        ],
        axisY: {
            labelInterpolationFnc: function (value) {
                return (value / 1) + 'k';
            }
        },
        showArea: false
    });


    var chart = [chart];

    var sparklineLogin = function () {
        $('#sparklinedash').sparkline([6, 4, 6, 10, 5, 5, 3, 3], {
            type: 'bar',
            height: '30',
            barWidth: '4',
            resize: true,
            barSpacing: '5',
            barColor: '#7ace4c'
        });
    }
    var sparkResize;
    $(window).on("resize", function (e) {
        clearTimeout(sparkResize);
        sparkResize = setTimeout(sparklineLogin, 5);
    });
    // sparklineLogin();
    $('#testbtn').click(function () {
        console.log('clickkato')
        sparklineLogin()
    })
});


