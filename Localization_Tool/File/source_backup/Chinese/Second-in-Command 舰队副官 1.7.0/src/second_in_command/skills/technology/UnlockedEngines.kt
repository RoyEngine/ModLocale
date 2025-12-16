package second_in_command.skills.technology

import com.fs.starfarer.api.combat.MutableShipStatsAPI
import com.fs.starfarer.api.combat.ShipAPI
import com.fs.starfarer.api.combat.ShipVariantAPI
import com.fs.starfarer.api.impl.campaign.ids.Stats
import com.fs.starfarer.api.ui.TooltipMakerAPI
import com.fs.starfarer.api.util.Misc
import second_in_command.SCData
import second_in_command.specs.SCBaseSkillPlugin

class UnlockedEngines : SCBaseSkillPlugin() {


    override fun getAffectsString(): String {
        return "舰队中所有舰船"
    }

    override fun addTooltip(data: SCData, tooltip: TooltipMakerAPI) {

        tooltip.addPara("根据船体级别，增加 20/20/15/10 最高航速", 0f, Misc.getHighlightColor(), Misc.getHighlightColor())


    }

    override fun applyEffectsBeforeShipCreation(data: SCData, stats: MutableShipStatsAPI?, variant: ShipVariantAPI, hullSize: ShipAPI.HullSize?, id: String?) {

        var increase = when(hullSize) {
            ShipAPI.HullSize.CAPITAL_SHIP -> 10f
            ShipAPI.HullSize.CRUISER -> 15f
            ShipAPI.HullSize.DESTROYER -> 20f
            ShipAPI.HullSize.FRIGATE -> 20f
            else -> 0f
        }

        stats!!.maxSpeed.modifyFlat(id, increase)

    }

    override fun applyEffectsAfterShipCreation(data: SCData, ship: ShipAPI?, variant: ShipVariantAPI, id: String?) {



    }



}