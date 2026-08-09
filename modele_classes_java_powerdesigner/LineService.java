package com.moovafrica.powerdesigner;

import jakarta.persistence.*;
import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.UUID;

@Entity
@Table(name = "line_services")
public class LineService {
    @Id
    private UUID id;

    @ManyToOne(optional = false)
    @JoinColumn(name = "line_id", nullable = false)
    private Line line; // Line 1 -> 0..* LineService

    @ManyToOne(optional = false)
    @JoinColumn(name = "service_id", nullable = false)
    private Service service; // Service 1 -> 0..* LineService

    private String codeOption;
    private LocalDateTime dateActivation;
    private LocalDateTime dateDesactivation;
    private boolean actif;
    private BigDecimal montantMensuel;
}
