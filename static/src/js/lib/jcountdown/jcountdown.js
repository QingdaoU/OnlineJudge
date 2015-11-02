/*! jCountdown jQuery Plugin - v2.0.0 - 2015-06-28
 * https://github.com/tomgrohl/jCountdown/
 * Copyright (c) 2015 Tom Ellis; Licensed MIT */
!function(root, factory) {
	if (typeof define === 'function' && define.amd) {
		define(['jquery'], factory);
	} else {
		factory(root.jQuery);
	}
}(this, function($) {

	$.fn.countdown = function( method /*, options*/ ) {

		var msPerHr = 3600000,
			secPerYear = 31557600,
			secPerMonth = 2629800,
			secPerWeek = 604800,
			secPerDay = 86400,
			secPerHr = 3600,
			secPerMin = 60,
			secPerSec = 1,
			rTemplateTokens = /%y|%m|%w|%d|%h|%i|%s|%ty|%tm|%tw|%td|%th|%ti|%ts/g,
			rDigitGlobal = /\d/g,
			localNumber = function( numToConvert, settings ) {

				var arr = numToConvert.toString().match(rDigitGlobal),
					localeNumber = "";

				$.each( arr, function(i,num) {
					num = Number(num);
					localeNumber += (""+ settings.digits[num]) || ""+num;
				});

				return localeNumber;
			},
			dateNow = function( $this ) {
				var now = new Date(), // Default to local time
					settings = $this.data("jcdData");

				if ( !settings ) {
					return new Date();
				}

				if ( settings.offset !== null ) {
					now = getTimezoneDate( settings.offset );
				}

				now.setMilliseconds(0);
				return now;
			},
			getTimezoneDate = function( offset ) {
				// Returns date now based on timezone/offset
				var hrs,
					dateMS,
					curHrs,
					tmpDate = new Date();

				if ( offset !== null ) {
					hrs = offset * msPerHr;
					curHrs = tmpDate.getTime() - ( ( -tmpDate.getTimezoneOffset() / 60 ) * msPerHr ) + hrs;
					dateMS = tmpDate.setTime( curHrs );
				}

				return new Date( dateMS );
			},
			addEventHandlers = function($element, options) {

				// Add event handlers where set
				if ( options.onStart ) {
					$element.on("start.jcdevt", options.onStart );
				}

				if ( options.onChange ) {
					$element.on("change.jcdevt", options.onChange );
				}

				if ( options.onComplete ) {
					$element.on("complete.jcdevt", options.onComplete );
				}

				if ( options.onPause ) {
					$element.on("pause.jcdevt", options.onPause );
				}

				if ( options.onResume ) {
					$element.on("resume.jcdevt", options.onResume );
				}

				if ( options.onLocaleChange ) {
					$element.on("locale.jcdevt", options.onLocaleChange );
				}
			},

			generateTemplate = function( settings ) {
				var template = settings.template,
					yearsLeft = settings.yearsLeft,
					monthsLeft = settings.monthsLeft,
					weeksLeft = settings.weeksLeft,
					daysLeft = settings.daysLeft,
					hrsLeft = settings.hrsLeft,
					minsLeft = settings.minsLeft,
					secLeft = settings.secLeft,
					hideYears = false,
					hideMonths = false,
					hideWeeks = false,
					hideDays = false,
					hideHours = false,
					hideMins = false;

				if (settings.isRTL) {
					template = settings.rtlTemplate;
				}

				if ( settings.omitZero ) {

					if ( settings.yearsAndMonths ) {

						if( !settings.yearsLeft ) {
							hideYears = true;
						}
						if( !settings.monthsLeft ) {
							hideMonths = true;
						}
					}

					if ( settings.weeks && ( ( settings.yearsAndMonths && hideMonths && !settings.weeksLeft ) || ( !settings.yearsAndMonths && !settings.weeksLeft ) ) ) {
						hideWeeks = true;
					}

					if ( hideWeeks && !daysLeft ) {
						hideDays = true;
					}

					if ( hideDays && !hrsLeft ) {
						hideHours = true;
					}

					if ( hideHours && !minsLeft ) {
						hideMins = true;
					}

				}

				if ( settings.leadingZero ) {

					if ( yearsLeft < 10 ) {
						yearsLeft = "0" + yearsLeft;
					}

					if ( monthsLeft < 10 ) {
						monthsLeft = "0" + monthsLeft;
					}

					if ( weeksLeft < 10 ) {
						weeksLeft = "0" + weeksLeft;
					}

					if ( daysLeft < 10 ) {
						daysLeft = "0" + daysLeft;
					}

					if ( hrsLeft < 10 ) {
						hrsLeft = "0" + hrsLeft;
					}

					if ( minsLeft < 10 ) {
						minsLeft = "0" + minsLeft;
					}

					if ( secLeft < 10 ) {
						secLeft = "0" + secLeft;
					}
				}

				yearsLeft = localNumber( yearsLeft, settings );
				monthsLeft = localNumber( monthsLeft, settings );
				weeksLeft = localNumber( weeksLeft, settings );
				daysLeft = localNumber( daysLeft, settings );
				hrsLeft = localNumber( hrsLeft, settings );
				minsLeft = localNumber( minsLeft, settings );
				secLeft = localNumber( secLeft, settings );

				if ( settings.yearsAndMonths ) {

					if ( !settings.omitZero || !hideYears  ) {
						template = template.replace('%y', yearsLeft);
						template = template.replace('%ty', (yearsLeft == 1 && settings.yearSingularText) ? settings.yearSingularText : settings.yearText);
					}

					//Only hide months if years is at 0 as well as months
					if ( !settings.omitZero || ( !hideYears && monthsLeft ) || ( !hideYears && !hideMonths ) ) {
						template = template.replace('%m', monthsLeft);
						template = template.replace('%tm', (monthsLeft == 1 && settings.monthSingularText) ? settings.monthSingularText : settings.monthText);
					}
				}

				if ( settings.weeks && !hideWeeks ) {
					template = template.replace('%w', weeksLeft);
					template = template.replace('%tw', (weeksLeft == 1 && settings.weekSingularText) ? settings.weekSingularText : settings.weekText);

				}

				if ( !hideDays ) {
					template = template.replace('%d', daysLeft);
					template = template.replace('%td', (daysLeft == 1 && settings.daySingularText) ? settings.daySingularText : settings.dayText);
				}

				if ( !hideHours ) {
					template = template.replace('%h', hrsLeft);
					template = template.replace('%th', (hrsLeft == 1 && settings.hourSingularText) ? settings.hourSingularText : settings.hourText);
				}

				if ( !hideMins ) {
					template = template.replace('%i', minsLeft);
					template = template.replace('%ti', (minsLeft == 1 && settings.minSingularText) ? settings.minSingularText : settings.minText);
				}

				template = template.replace('%s', secLeft);
				template = template.replace('%ts', (secLeft == 1 && settings.secSingularText) ? settings.secSingularText : settings.secText);

				// Remove un-used tokens
				template = template.replace(rTemplateTokens,'');

				return template;
			},
			updateCallback = function() {

				var $this = this,
					template,
					now,
					date,
					timeLeft,
					yearsLeft = 0,
					monthsLeft = 0,
					weeksLeft = 0,
					daysLeft,
					hrsLeft,
					minsLeft,
					secLeft,
					time = "",
					diff,
					extractSection = function( numSecs ) {
						var amount;

						amount = Math.floor( diff / numSecs );
						diff -= amount * numSecs;

						return amount;
					},
					settings = $this.data("jcdData");

				// No settings so return
				if ( !settings ) {
					return false;
				}

				now = dateNow( $this );

				if ( null !== settings.serverDiff ) {
					date = new Date( settings.serverDiff + settings.clientdateNow.getTime() );
				}
				else {
					date = settings.dateObj;
				}

				date.setMilliseconds(0);

				timeLeft = ( settings.direction === "down" ) ? date.getTime() - now.getTime() : now.getTime() - date.getTime();

				diff = Math.round( timeLeft / 1000 );

				daysLeft = extractSection( secPerDay );
				hrsLeft = extractSection( secPerHr );
				minsLeft = extractSection( secPerMin );
				secLeft = extractSection( secPerSec );

				if ( settings.yearsAndMonths ) {

					//Add days back on so we can calculate years easier
					diff += ( daysLeft * secPerDay );

					yearsLeft = extractSection( secPerYear );
					monthsLeft = extractSection( secPerMonth );
					daysLeft = extractSection( secPerDay );
				}

				if ( settings.weeks ) {
					//Add days back on so we can calculate weeks easier
					diff += ( daysLeft * secPerDay );

					weeksLeft = extractSection( secPerWeek );
					daysLeft = extractSection( secPerDay );
				}

				/**
				 * The following 3 option should never be used together!
				 * MAKE them work for any time
				 */

				if ( settings.hoursOnly || settings.minsOnly || settings.secsOnly )
				{

					if ( settings.yearsAndMonths ) {
						//Add years, months, weeks and days back on so we can calculate dates easier
						diff += ( yearsLeft * secPerYear );
						diff += ( monthsLeft * secPerMonth );

						yearsLeft = monthsLeft = 0;
					}

					if ( settings.weeks ) {
						diff += ( weeksLeft * secPerWeek );

						weeksLeft = 0;
					}

				}

				// Assumes you are using dates within a month  ( ~ 30 days )
				// as years and months aren't taken into account
				if ( settings.hoursOnly ) {

					// Add days back on
					diff += ( daysLeft * secPerDay );

					// Add hours back on
					diff += ( hrsLeft * secPerHr );
					hrsLeft = extractSection( secPerHr );

				}

				// Assumes you are only using dates in the near future ( <= 24 hours )
				// as years and months aren't taken into account
				if ( settings.minsOnly ) {


					// Add days back on
					diff += ( daysLeft * secPerDay );
					daysLeft = 0;

					// Add hours back on
					diff += ( hrsLeft * secPerHr );
					hrsLeft = 0;

					diff += ( minsLeft * secPerMin );

					minsLeft = extractSection( secPerMin );

				}

				// Assumes you are only using dates in the near future ( <= 60 minutes )
				// as years, months and days aren't taken into account
				if ( settings.secsOnly ) {


					// Add days back on
					diff += ( daysLeft * secPerDay );
					daysLeft = 0;

					// Add hours back on
					diff += ( hrsLeft * secPerHr );
					hrsLeft = 0;

					// Add minutes back on
					diff += ( minsLeft * secPerMin );
					minsLeft = 0;

					// Add seconds back on
					diff += secLeft;

					secLeft = extractSection( secPerSec );
				}

				settings.yearsLeft = yearsLeft;
				settings.monthsLeft = monthsLeft;
				settings.weeksLeft = weeksLeft;
				settings.daysLeft = daysLeft;
				settings.hrsLeft = hrsLeft;
				settings.minsLeft = minsLeft;
				settings.secLeft = secLeft;

				$this.data("jcdData", settings);

				// Check if the countdown has finished
				if ( !( settings.direction === "down" && ( now < date || settings.minus ) ) || !( settings.direction === "up" && ( date < now || settings.minus )  ) ) {
					//settings.yearsLeft = settings.monthsLeft = settings.weeksLeft = settings.daysLeft = settings.hrsLeft = settings.minsLeft = settings.secLeft = 0;
					//settings.hasCompleted = true;
				}

				// We've got the time sections set so we can now do the templating

				if ( ( settings.direction === "down" && ( now < date || settings.minus ) ) || ( settings.direction === "up" && ( date < now || settings.minus )  ) ) {
					time = generateTemplate( settings );
				}
				else {
					settings.yearsLeft = settings.monthsLeft = settings.weeksLeft = settings.daysLeft = settings.hrsLeft = settings.minsLeft = settings.secLeft = 0;

					time = generateTemplate( settings );
					settings.hasCompleted = true;
				}

				$this.html( time ).triggerMulti("change.jcdevt,countChange", [settings]);

				if ( settings.hasCompleted ) {
					$this.triggerMulti("complete.jcdevt,countComplete");
					clearInterval( settings.timer );
				}

			},
			methods = {
				init: function( options ) {
					var opts = $.extend( {}, $.fn.countdown.defaults, options ),
						testDate,
						testString,
						settings = {};

					return this.each(function() {

						var $this = $(this),
							intervalCallback;

						// If this element already has a countdown timer
						// just change the settings
						if ( $this.data("jcdData") ) {
							$this.countdown("changeSettings", options, true);
							opts = $this.data("jcdData");
						}

						if ( opts.date === null && opts.dataAttr === null ) {
							$.error("No Date passed to jCountdown. date option is required.");
							return true;
						}

						if ( opts.date ) {
							testString = opts.date;
						} else {
							testString = $this.data(opts.dataAttr);
						}

						testDate = new Date(testString);

						if( testDate.toString() === "Invalid Date" ) {
							$.error("Invalid Date passed to jCountdown: " + testString);
						}

						// Setup any event handlers
						addEventHandlers($this, options);

						// Create a settings object based off the plugin options
						settings = $.extend({}, opts);

						// Cache DOM elements for templating
						settings.dom = {};

						settings.dom.$time = $("<"+settings.timeWrapElement+">").addClass(settings.timeWrapClass);
						settings.dom.$text = $("<"+settings.textWrapElement+">").addClass(settings.textWrapClass);

						settings.clientdateNow = new Date();
						settings.clientdateNow.setMilliseconds(0);
						settings.originalHTML = $this.html();
						settings.dateObj = new Date( testString );
						settings.dateObj.setMilliseconds(0);
						settings.hasCompleted = false;
						settings.timer = 0;
						settings.yearsLeft = settings.monthsLeft = settings.weeksLeft = settings.daysLeft = settings.hrsLeft = settings.minsLeft = settings.secLeft = 0;
						settings.difference = null;

						// Create a callback for the interval
						intervalCallback = $.proxy(updateCallback, $this);
						settings.timer = setInterval(intervalCallback, settings.updateTime);

						$this.data("jcdData", settings).triggerMulti("start.jcdevt,countStart", [settings]);

						intervalCallback();

					});
				},
				changeSettings: function( options, internal ) {

					// Like resume but with resetting/changing options
					return this.each(function() {
						var $this  = $(this),
							settings,
							testDate,
							func = $.proxy( updateCallback, $this );

						if ( !$this.data("jcdData") ) {
							return true;
						}

						settings = $.extend( {}, $this.data("jcdData"), options );

						if ( options.hasOwnProperty("date") ) {
							testDate = new Date(options.date);

							if ( testDate.toString() === "Invalid Date" ) {
								$.error("Invalid Date passed to jCountdown: " + options.date);
							}
						}

						settings.completed = false;
						settings.dateObj  = new Date( options.date );

						// Clear the timer, as it might not be needed
						clearInterval( settings.timer );
						$this.off(".jcdevt").data("jcdData", settings);

						// As this can be accessed via the init method as well,
						// we need to check how this method is being accessed
						if ( !internal ) {

							addEventHandlers($this, settings);

							settings.timer = setInterval( func, settings.updateTime );
							$this.data("jcdData", settings);
							func(); //Needs to run straight away when changing settings
						}

						settings = null;
					});

				},
				resume: function() {

					// Resumes a countdown timer
					return this.each(function() {
						var $this = $(this),
							settings = $this.data("jcdData"),
							func = $.proxy( updateCallback, $this );

						if ( !settings ) {
							return true;
						}

						$this.data("jcdData", settings).triggerMulti("resume.jcdevt,countResume", [settings] );
						// We only want to resume a countdown that hasn't finished
						if ( !settings.hasCompleted ) {
							settings.timer = setInterval( func, settings.updateTime );

							if ( settings.stopwatch && settings.direction === "up" ) {

								var t = dateNow( $this ).getTime() - settings.pausedAt.getTime(),
									d = new Date();
								d.setTime( settings.dateObj.getTime() + t );

								settings.dateObj = d; //This is internal date
							}

							func();
						}
					});

				},
				pause: function() {
					// Pause a countdown timer
					return this.each(function() {
						var $this = $(this),
							settings = $this.data("jcdData");

						if ( !settings ) {
							return true;
						}

						if ( settings.stopwatch ) {
							settings.pausedAt = dateNow( $this );
						}
						// Clear interval (Will be started on resume)
						clearInterval( settings.timer );
						// Trigger pause event handler
						$this.data("jcdData", settings).triggerMulti("pause.jcdevt,countPause", [settings] );
					});
				},
				complete: function() {
					return this.each(function() {
						var $this = $(this),
							settings = $this.data("jcdData");

						if ( !settings ) {
							return true;
						}
						// Clear timer
						clearInterval( settings.timer );
						settings.hasCompleted = true;
						// Update setting, trigger complete event handler, then unbind all events
						// We don"t delete the settings in case they need to be checked later on

						$this.data("jcdData", settings).triggerMulti("complete.jcdevt,countComplete", [settings]);
					});
				},
				destroy: function() {
					return this.each(function() {
						var $this = $(this),
							settings = $this.data("jcdData");

						if ( !settings ) {
							return true;
						}
						// Clear timer
						clearInterval( settings.timer );
						// Unbind all events, remove data and put DOM Element back to its original state (HTML wise)
						$this.off(".jcdevt").removeData("jcdData").html( settings.originalHTML );
					});
				},
				getSettings: function( name ) {
					var $this = $(this),
						settings = $this.data("jcdData");

					// If an individual setting is required
					if ( name && settings ) {
						// If it exists, return it
						if ( settings.hasOwnProperty( name ) ) {
							return settings[name];
						}
						return undefined;
					}
					// Return all settings or undefined
					return settings;
				},
				changeLocale: function( locale ) {
					var $this = $(this),
						settings = $this.data("jcdData");

					// If no locale exists error and return false
					if ( !$.fn.countdown.locale[locale] ) {
						$.error("Locale '" + locale + "' does not exist");
						return false;
					}

					$.extend( settings, $.fn.countdown.locale[locale] );

					$this.data("jcdData", settings).triggerMulti("locale.jcdevt,localeChange", [settings]);

					return true;
				}
			};

		if( methods[ method ] ) {
			return methods[ method ].apply( this, Array.prototype.slice.call( arguments, 1 ) );
		} else if ( typeof method === "object" || !method ) {
			return methods.init.apply( this, arguments );
		} else {
			$.error("Method "+ method +" does not exist in the jCountdown Plugin");
		}
	};

// Expose defaults so we can easily override settings
// Useful for locale plugins
	$.fn.countdown.defaults = {
		date: null,
		dataAttr: null,
		updateTime: 1000,
		yearText: 'years',
		monthText: 'months',
		weekText: 'weeks',
		dayText: '天',
		hourText: '小时',
		minText: '分',
		secText: '秒',
		yearSingularText: 'year',
		monthSingularText: 'month',
		weekSingularText: 'week',
		daySingularText: '天',
		hourSingularText: '小时',
		minSingularText: '分钟',
		secSingularText: '秒',
		digits : [0,1,2,3,4,5,6,7,8,9],
		isRTL: false,
		minus: false,
		onStart: null,
		onChange: null,
		onComplete: null,
		onResume: null,
		onPause: null,
		onLocaleChange: null,
		leadingZero: false,
		offset: null,
		serverDiff:null,
		hoursOnly: false,
		minsOnly: false,
		secsOnly: false,
		weeks: false,
		hours: false,
		yearsAndMonths: false,
		direction: "down",
		stopwatch: false,
		omitZero: false,

		rtlTemplate: '%ts %s : %ti %i : %th %h : %tm %m : %ty %y',
		template: '%y %ty : %m %tm : %h %th : %i %ti : %s %ts'
	};

// Locale cache
	$.fn.countdown.locale = [];

// Store default english locale so we can switch easier
	$.fn.countdown.locale.en = {
		yearText: '年',
		monthText: '月',
		weekText: '星期',
		dayText: '天',
		hourText: '小时',
		minText: '分钟',
		secText: '秒',
		yearSingularText: '年',
		monthSingularText: '月',
		weekSingularText: '星期',
		daySingularText: '天',
		hourSingularText: '小时',
		minSingularText: '分钟',
		secSingularText: '秒',
		isRTL: false
	};

//
	$.fn.triggerMulti = function( eventTypes, extraParameters ) {
		var events = eventTypes.split(",");

		return this.each(function() {
			var $this = $(this);

			for ( var i = 0; i < events.length; i++) {
				$this.trigger( events[i], extraParameters );
			}
		});
	};

});
