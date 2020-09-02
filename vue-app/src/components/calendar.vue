<template>
  <div class="calendar">
    <header class="header">
        <button @click="previousMonth">&lt;&lt;</button>
        <span>{{ currentMonthLabel }} {{ currentYear }}</span>
        <button @click="nextMonth">&gt;&gt;</button>
    </header>
    <div class="headings" v-for="dayLabel in dayLabels" v-bind:key="dayLabel.id">
        {{ dayLabel }}
    </div>
    <div v-for="(day, index) in dates"
        class="day"
        :class="dayClassObj(day)" v-bind:key="index">
        <button @click="setSelectedDate(day)">
        {{ day.date | formatDateToDay }}
        </button>
    </div>
</div>
</template>

<style lang="scss">
:root {
  --white: hsl(0, 0%, 100%);
  --blue-grey-400: hsl(210, 38%, 95%);
  --blue-grey-100: hsl(210, 38%, 80%);
  --black-400: hsl(0, 0%, 96%);
  --black-300: hsl(0, 0%, 85%);
  --black-200: hsl(0, 0%, 75%);
  --black-100: hsl(0, 0%, 20%);
}

html {
  box-sizing: border-box;
  font-size: 16px;
}

*,
*:before,
*:after {
  box-sizing: inherit;
  font-family: inherit;
}

html,
body {
  height: 100%;
  width: 100%;
  overflow: hidden;
}

body {
  font-family: 'Inconsolata', serif;
  background: var(--blue-grey-400);
  color: var(--black-100);
  display: flex;
  justify-content: center;
}

.calendar {
  background-color: var(--white);
  border-radius: 3px;
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  width: 300px;
  padding: .25rem .5rem 1rem .5rem;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  
  > .top {
    grid-column: 1 / span 7;
  }

  > .header {
    padding: .75rem;
    font-size: 1.25rem;
    grid-column: 1 / span 7;
    
    >span {
      flex: 1;
      text-align: center;
    }
    
    button {
      border: none;
      background: var(--white);
      margin: 0 1rem;
      padding: .25rem .5rem;
      
      :hover {
        background: var(--black-400);
        transition: background 150ms;
      }
    }
  }

  > * {
    align-items: center;
    display: flex;
    justify-content: center;
  }

  > .day {
    color: var(--black-200);
    font-size: 1rem;
    border-radius: 2px;
    
    &.selected {
      border: 1px solid var(--blue-grey-100);
    }
    
    &.current {
      color: var(--black-100);
    }

    &::before {
      content: "";
      display: inline-block;
      height: 0;
      padding-bottom: 100%;
      width: 1px;
    }
    
    button {
      color: inherit;
      background: transparent;
      border: none;
      height: 100%;
      width: 100%;
      &:hover {
        background: var(--black-400);
        transition: background 150ms;
      }
    }
  }

  > .today {
    background: var(--black-400);
    border-radius: 2px;
  }
}



.text-center {
  text-align: center;
}
</style>

<script src="http://cdn.date-fns.org/VERSION/date_fns.min.js"></script>
<script>
import {startOfMonth, lastDayOfMonth, isSameMonth, getDay, addDays, eachDay, isToday, isSameDay, addMonths, getMonth, setMonth, format } from 'date-fns'

export default {
    name: 'calendar',
    data() {
        return {
            today: null,
            selectedDate: null,
            currDateCursor: null,
            dayLabels: null,
            DAY_LABELS: ['S', 'M', 'T', 'W', 'Th', 'F', 'S'],
            MONTH_LABELS: [
                "January", "February", "March",
                "April", "May", "June",
                "July", "August", "September",
                "October", "November", "December"],
            };
    },
    created() {
        this.dayLabels = this.DAY_LABELS.slice();
        this.today = new Date(2016, 8, 1);
        console.log(this.today)
        this.selectedDate = this.today;
        this.currDateCursor = this.today;
    },
    props: {
        startDate: {
            required: false,
            type: Date,
        }
    },
    computed: {
        currentMonth() {
            return this.currDateCursor.getMonth();
        },
        currentYear() {
            return this.currDateCursor.getFullYear();
        },
        currentMonthLabel() {
            return this.MONTH_LABELS[this.currentMonth];
        },
        dates() {
            const cursorDate = this.currDateCursor;
            let startDate = startOfMonth(cursorDate),
                endDate = lastDayOfMonth(cursorDate);
            const daysNeededForLastMonth = getDay(startDate),
                    daysNeededForNextMonth = (7 - (getDay(endDate) + 1)) > 6 ? 0 : (7 - getDay(endDate)) - 1;
            startDate = addDays(startDate, -daysNeededForLastMonth);
            endDate = addDays(endDate, daysNeededForNextMonth);
            // console.log(eachDay(startDate, endDate));
            
            return eachDay(startDate, endDate)
            .map(date => ({
                date,
                isCurrentMonth:  isSameMonth(cursorDate, date),
                isToday: isToday(date),
                isSelected: isSameDay(this.selectedDate, date)  
            }));
        },
    },
    mounted() {
        if (this.startDate) {
        this.currDateCursor = this.startDate;
        this.selectedDate = this.startDate;
        }
    },
    methods: {
        dayClassObj(day) {
            return {
                'today' : day.isToday,
                'current': day.isCurrentMonth,
                'selected': day.isSelected,
            };
        },
        nextMonth() {
            this.currDateCursor = addMonths(this.currDateCursor, 1);
            this.$emit('dateSelected', this.currDateCursor);
        },
        previousMonth() {
            this.currDateCursor = addMonths(this.currDateCursor, -1);
            this.$emit('dateSelected', this.currDateCursor);
        },
        setSelectedDate(day) {
            this.selectedDate = day.date;

            this.$emit('dateSelected', this.selectedDate);
            // change calendar to correct month if they select previous or next month's days
            if (!day.isCurrentMonth) {
                const selectedMonth = getMonth(this.selectedDate);
                this.currDateCursor = setMonth(this.currDateCursor, selectedMonth);
            }
        }
    },
    filters: {
        formatDateToDay(val) {
            return format(val, 'D');
        }
    },
}

</script>