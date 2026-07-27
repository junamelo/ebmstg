import { useState, useRef, useEffect } from 'react'
import './DateRangePicker.css'

const MONTHS = [
  'Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin',
  'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre'
]

const DAYS = ['Dim', 'Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam']

function DateRangePicker({ value, onChange, placeholder = "Sélectionner une période" }) {
  const [isOpen, setIsOpen] = useState(false)
  const [currentMonth, setCurrentMonth] = useState(new Date())
  const [startDate, setStartDate] = useState(value?.start || null)
  const [endDate, setEndDate] = useState(value?.end || null)
  const [hoverDate, setHoverDate] = useState(null)
  const pickerRef = useRef(null)

  useEffect(() => {
    function handleClickOutside(event) {
      if (pickerRef.current && !pickerRef.current.contains(event.target)) {
        setIsOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const getDaysInMonth = (date) => {
    const year = date.getFullYear()
    const month = date.getMonth()
    const firstDay = new Date(year, month, 1)
    const lastDay = new Date(year, month + 1, 0)
    const startDate = new Date(firstDay)
    
    // Commencer au dimanche précédent
    startDate.setDate(startDate.getDate() - startDate.getDay())
    
    const days = []
    const current = new Date(startDate)
    
    // Générer 42 jours (6 semaines)
    for (let i = 0; i < 42; i++) {
      days.push({
        date: new Date(current),
        isCurrentMonth: current.getMonth() === month,
        isToday: current.toDateString() === new Date().toDateString()
      })
      current.setDate(current.getDate() + 1)
    }
    
    return days
  }

  const formatDateForDisplay = (date) => {
    if (!date) return null
    return date.toLocaleDateString('fr-FR', {
      day: '2-digit',
      month: '2-digit', 
      year: 'numeric'
    })
  }

  const isDateInRange = (date) => {
    if (!startDate || !endDate) return false
    return date >= startDate && date <= endDate
  }

  const isDateInHoverRange = (date) => {
    if (!startDate || !hoverDate || endDate) return false
    const start = startDate < hoverDate ? startDate : hoverDate
    const end = startDate < hoverDate ? hoverDate : startDate
    return date >= start && date <= end
  }

  const handleDateClick = (date) => {
    if (!startDate || (startDate && endDate)) {
      // Première date ou reset
      setStartDate(date)
      setEndDate(null)
      setHoverDate(null)
    } else {
      // Deuxième date
      if (date < startDate) {
        setEndDate(startDate)
        setStartDate(date)
      } else {
        setEndDate(date)
      }
      setHoverDate(null)
      
      // Fermer le picker et appeler onChange
      setTimeout(() => {
        setIsOpen(false)
        if (onChange) {
          onChange({
            start: date < startDate ? date : startDate,
            end: date < startDate ? startDate : date
          })
        }
      }, 150)
    }
  }

  const handleDateHover = (date) => {
    if (startDate && !endDate) {
      setHoverDate(date)
    }
  }

  const navigateMonth = (direction) => {
    setCurrentMonth(prev => {
      const newDate = new Date(prev)
      newDate.setMonth(prev.getMonth() + direction)
      return newDate
    })
  }

  const clearSelection = () => {
    setStartDate(null)
    setEndDate(null)
    setHoverDate(null)
    if (onChange) {
      onChange({ start: null, end: null })
    }
  }

  const getDisplayText = () => {
    if (startDate && endDate) {
      return `${formatDateForDisplay(startDate)} - ${formatDateForDisplay(endDate)}`
    } else if (startDate) {
      return `${formatDateForDisplay(startDate)} - ...`
    }
    return placeholder
  }

  const days = getDaysInMonth(currentMonth)

  return (
    <div className="date-range-picker" ref={pickerRef}>
      <div 
        className={`date-input ${isOpen ? 'active' : ''}`}
        onClick={() => setIsOpen(!isOpen)}
      >
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <rect x="3" y="4" width="18" height="18" rx="2"/>
          <line x1="16" y1="2" x2="16" y2="6"/>
          <line x1="8" y1="2" x2="8" y2="6"/>
          <line x1="3" y1="10" x2="21" y2="10"/>
        </svg>
        <span className={startDate ? 'has-value' : 'placeholder'}>
          {getDisplayText()}
        </span>
        {(startDate || endDate) && (
          <button 
            type="button"
            className="clear-btn"
            onClick={(e) => {
              e.stopPropagation()
              clearSelection()
            }}
          >
            ✕
          </button>
        )}
      </div>

      {isOpen && (
        <div className="date-picker-dropdown">
          <div className="picker-header">
            <button 
              type="button"
              className="nav-btn"
              onClick={() => navigateMonth(-1)}
            >
              ‹
            </button>
            <div className="month-year">
              {MONTHS[currentMonth.getMonth()]} {currentMonth.getFullYear()}
            </div>
            <button 
              type="button"
              className="nav-btn"
              onClick={() => navigateMonth(1)}
            >
              ›
            </button>
          </div>

          <div className="picker-calendar">
            <div className="days-header">
              {DAYS.map(day => (
                <div key={day} className="day-name">{day}</div>
              ))}
            </div>

            <div className="days-grid">
              {days.map((day, index) => {
                const isSelected = (startDate && day.date.toDateString() === startDate.toDateString()) || 
                                 (endDate && day.date.toDateString() === endDate.toDateString())
                const isInRange = isDateInRange(day.date)
                const isInHoverRange = isDateInHoverRange(day.date)
                
                return (
                  <button
                    key={index}
                    type="button"
                    className={`day-cell ${!day.isCurrentMonth ? 'other-month' : ''} ${
                      day.isToday ? 'today' : ''
                    } ${isSelected ? 'selected' : ''} ${
                      isInRange ? 'in-range' : ''
                    } ${isInHoverRange ? 'hover-range' : ''}`}
                    onClick={() => handleDateClick(day.date)}
                    onMouseEnter={() => handleDateHover(day.date)}
                  >
                    {day.date.getDate()}
                  </button>
                )
              })}
            </div>
          </div>

          <div className="picker-footer">
            <button type="button" className="btn-clear" onClick={clearSelection}>
              Effacer
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

export default DateRangePicker