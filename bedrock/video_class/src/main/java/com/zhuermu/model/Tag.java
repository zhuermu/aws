package com.zhuermu.model;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Data;

@Data
public class Tag {
    @JsonProperty("tag")
    private String name;
    
    @JsonProperty("scores")
    private Integer score;
}
