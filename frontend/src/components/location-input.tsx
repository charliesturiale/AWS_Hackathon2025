"use client"

import { useState, useEffect, useRef } from "react"
import { Input } from "@/components/ui/input"
import { MapPin, Star, X, Search, Loader2 } from "lucide-react"
import { getSavedLocations, searchLocations, deleteLocation, type SavedLocation } from "@/services/savedLocations"
import { searchAddresses, formatAddress, type AddressSuggestion } from "@/services/geocoding"
import { cn } from "@/lib/utils"

interface LocationInputProps {
  value: string
  onChange: (value: string) => void
  placeholder: string
  icon: React.ReactNode
  className?: string
}

export default function LocationInput({ value, onChange, placeholder, icon, className }: LocationInputProps) {
  const [showDropdown, setShowDropdown] = useState(false)
  const [savedLocations, setSavedLocations] = useState<SavedLocation[]>([])
  const [filteredLocations, setFilteredLocations] = useState<SavedLocation[]>([])
  const [addressSuggestions, setAddressSuggestions] = useState<AddressSuggestion[]>([])
  const [isSearching, setIsSearching] = useState(false)
  const dropdownRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)
  const debounceTimerRef = useRef<NodeJS.Timeout | null>(null)

  // Load saved locations
  useEffect(() => {
    const locations = getSavedLocations()
    setSavedLocations(locations)
  }, [])

  // Filter saved locations and fetch address suggestions
  useEffect(() => {
    // Clear previous debounce timer
    if (debounceTimerRef.current) {
      clearTimeout(debounceTimerRef.current)
    }

    if (value.trim()) {
      // Filter saved locations immediately
      const filtered = searchLocations(value)
      setFilteredLocations(filtered)

      // Debounce address API search (500ms delay)
      if (value.trim().length >= 3) {
        setIsSearching(true)
        debounceTimerRef.current = setTimeout(async () => {
          const suggestions = await searchAddresses(value.trim())
          setAddressSuggestions(suggestions)
          setIsSearching(false)
        }, 500)
      } else {
        setAddressSuggestions([])
        setIsSearching(false)
      }
    } else {
      // Show all saved locations when input is empty
      setFilteredLocations(savedLocations.slice(0, 5))
      setAddressSuggestions([])
      setIsSearching(false)
    }

    // Cleanup function
    return () => {
      if (debounceTimerRef.current) {
        clearTimeout(debounceTimerRef.current)
      }
    }
  }, [value, savedLocations])

  // Handle click outside to close dropdown
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(event.target as Node) &&
        inputRef.current &&
        !inputRef.current.contains(event.target as Node)
      ) {
        setShowDropdown(false)
      }
    }

    document.addEventListener("mousedown", handleClickOutside)
    return () => document.removeEventListener("mousedown", handleClickOutside)
  }, [])

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    onChange(e.target.value)
    setShowDropdown(true)
  }

  const handleSelectLocation = (location: SavedLocation) => {
    onChange(location.address)
    setShowDropdown(false)
  }

  const handleSelectAddressSuggestion = (suggestion: AddressSuggestion) => {
    const formattedAddress = formatAddress(suggestion.display_name)
    onChange(formattedAddress)
    setShowDropdown(false)
  }

  const handleDeleteLocation = (e: React.MouseEvent, id: string) => {
    e.stopPropagation()
    deleteLocation(id)
    const updated = getSavedLocations()
    setSavedLocations(updated)
  }

  const handleFocus = () => {
    setShowDropdown(true)
  }

  return (
    <div className="relative">
      <div className="relative">
        {icon}
        <Input
          ref={inputRef}
          placeholder={placeholder}
          value={value}
          onChange={handleInputChange}
          onFocus={handleFocus}
          className={cn("pl-10 h-11 border-2", className)}
        />
      </div>

      {/* Dropdown */}
      {showDropdown && (filteredLocations.length > 0 || addressSuggestions.length > 0 || isSearching) && (
        <div
          ref={dropdownRef}
          className="absolute z-50 w-full mt-2 bg-white border-2 border-border rounded-xl shadow-lg max-h-80 overflow-y-auto"
        >
          <div className="py-2">
            {/* Saved Locations Section */}
            {filteredLocations.length > 0 && (
              <div className="mb-2">
                <div className="px-3 py-2 text-xs font-semibold text-muted-foreground flex items-center gap-1.5">
                  <Star className="h-3 w-3" />
                  Saved Locations
                </div>
                {filteredLocations.map((location) => (
                  <button
                    key={location.id}
                    onClick={() => handleSelectLocation(location)}
                    className="w-full px-3 py-2.5 text-left hover:bg-primary/10 transition-colors flex items-start gap-3 group"
                  >
                    <MapPin className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
                    <div className="flex-1 min-w-0">
                      <div className="font-medium text-sm text-foreground truncate">{location.name}</div>
                      {location.name !== location.address && (
                        <div className="text-xs text-muted-foreground truncate">{location.address}</div>
                      )}
                    </div>
                    <button
                      onClick={(e) => handleDeleteLocation(e, location.id)}
                      className="opacity-0 group-hover:opacity-100 transition-opacity p-1 hover:bg-destructive/10 rounded"
                      title="Remove location"
                    >
                      <X className="h-3.5 w-3.5 text-destructive" />
                    </button>
                  </button>
                ))}
              </div>
            )}

            {/* Loading State */}
            {isSearching && (
              <div className="px-3 py-4 flex items-center justify-center gap-2 text-muted-foreground">
                <Loader2 className="h-4 w-4 animate-spin" />
                <span className="text-sm">Searching addresses...</span>
              </div>
            )}

            {/* Address Suggestions Section */}
            {!isSearching && addressSuggestions.length > 0 && (
              <div>
                {filteredLocations.length > 0 && (
                  <div className="border-t border-border/50 my-2" />
                )}
                <div className="px-3 py-2 text-xs font-semibold text-muted-foreground flex items-center gap-1.5">
                  <Search className="h-3 w-3" />
                  Address Suggestions
                </div>
                {addressSuggestions.map((suggestion) => (
                  <button
                    key={suggestion.place_id}
                    onClick={() => handleSelectAddressSuggestion(suggestion)}
                    className="w-full px-3 py-2.5 text-left hover:bg-accent/10 transition-colors flex items-start gap-3"
                  >
                    <MapPin className="h-4 w-4 text-accent mt-0.5 flex-shrink-0" />
                    <div className="flex-1 min-w-0">
                      <div className="font-medium text-sm text-foreground truncate">
                        {formatAddress(suggestion.display_name)}
                      </div>
                      <div className="text-xs text-muted-foreground truncate">
                        {suggestion.type}
                      </div>
                    </div>
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
