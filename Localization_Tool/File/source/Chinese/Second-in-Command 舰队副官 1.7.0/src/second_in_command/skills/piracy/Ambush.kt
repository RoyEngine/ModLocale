package second_in_command.skills.piracy

import com.fs.starfarer.api.combat.MutableShipStatsAPI
import com.fs.starfarer.api.combat.ShipAPI
import com.fs.starfarer.api.combat.ShipVariantAPI
import com.fs.starfarer.api.impl.campaign.ids.Stats
import com.fs.starfarer.api.impl.campaign.skills.Sensors
import com.fs.starfarer.api.ui.TooltipMakerAPI
import com.fs.starfarer.api.util.Misc
import second_in_command.SCData
import second_in_command.specs.SCBaseSkillPlugin

class Ambush : SCBaseSkillPlugin() {

    override fun getAffectsString(): String {
        return "舰队"
    }

    override fun addTooltip(data: SCData, tooltip: TooltipMakerAPI) {

        tooltip.addPara("-25%% 被探测范围", 0f, Misc.getHighlightColor(), Misc.getHighlightColor())
        tooltip.addPara("+3 当舰队处于 缓速航行* 时的最大宇宙航行速度", 0f, Misc.getHighlightColor(), Misc.getHighlightColor())

        tooltip.addSpacer(10f)

        tooltip.addPara("*缓速航行的舰队在某些地形中更难被发现，并且可以避免某些危险。有些能力能够减慢" +
                "舰队的航行速度。当舰队的移动速度为舰队中最慢舰船的最大宇宙航速的一半时，该舰队视作 缓速航行。", 0f, Misc.getGrayColor(), Misc.getHighlightColor())

    }

    override fun applyEffectsBeforeShipCreation(data: SCData, stats: MutableShipStatsAPI?, variant: ShipVariantAPI, hullSize: ShipAPI.HullSize?, id: String?) {


    }

    override fun applyEffectsAfterShipCreation(data: SCData, ship: ShipAPI?, variant: ShipVariantAPI, id: String?) {



    }

    override fun advance(data: SCData, amount: Float) {
        data.fleet.stats.detectedRangeMod.modifyMult("sc_ambush", 0.75f, "暗中伏击")
        data.fleet.stats.dynamic.getMod(Stats.MOVE_SLOW_SPEED_BONUS_MOD).modifyFlat("sc_ambush", 3f, "暗中伏击")
    }

    override fun onActivation(data: SCData) {
        data.fleet.stats.detectedRangeMod.modifyMult("sc_ambush", 0.75f, "暗中伏击")
        data.fleet.stats.dynamic.getMod(Stats.MOVE_SLOW_SPEED_BONUS_MOD).modifyFlat("sc_ambush", 3f, "暗中伏击")
    }

    override fun onDeactivation(data: SCData) {
        data.fleet.stats.detectedRangeMod.unmodify("sc_ambush")
        data.fleet.stats.dynamic.getMod(Stats.MOVE_SLOW_SPEED_BONUS_MOD).unmodify("sc_ambush")
    }

}